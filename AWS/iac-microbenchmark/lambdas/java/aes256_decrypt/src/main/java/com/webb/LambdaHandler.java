package com.webb;

import java.util.Map;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.util.HashMap;
import java.nio.charset.StandardCharsets;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.services.kms.model.DecryptRequest;
import software.amazon.awssdk.services.kms.model.DecryptResponse;
import software.amazon.awssdk.regions.Region;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Base64;
public class LambdaHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    // Create an instance of ObjectMapper for JSON parsing and serialization
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private KmsClient kmsClient;

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
        context.getLogger().log("Received event: " + request);

          // Create a response object
          APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent();
          HashMap<String,String> rspHeaders = new HashMap<>();
          rspHeaders.put("Access-Control-Allow-Origin", "*");
          rspHeaders.put("Content-Type", "application/json");
          response.setHeaders(rspHeaders);

        try {
        	
            // Get KMS key ARN from environment variables
            String Aes256DecryptKmsKeyId = System.getenv("AES_KMS_KEY_ARN");
        	
            // Get the JSON string from the request body
            String body = request.getBody();
                    
            // Deserialize the request body into Sha256RequestMessage object

            //
            Aes256DecryptRequestMessage requestMessage = objectMapper.readValue(body, Aes256DecryptRequestMessage.class);

            // Decrypt the encrypted key using KMS
            byte[] encryptedKeyBytes = Base64.getDecoder().decode(requestMessage.getEncrypted_key());
            // Decode IV, tag, and ciphertext
            byte[] iv = Base64.getDecoder().decode(requestMessage.getIv());
            byte[] tag = Base64.getDecoder().decode(requestMessage.getTag());
            byte[] ciphertext = Base64.getDecoder().decode(requestMessage.getCiphertext());
            byte[] ciphertextWithTag = new byte[ciphertext.length + tag.length];
            
            try {
            	 SdkBytes encryptedKey = SdkBytes.fromByteArray(encryptedKeyBytes);

                 DecryptRequest decryptRequest = DecryptRequest.builder()
                         .keyId(Aes256DecryptKmsKeyId)
                         .ciphertextBlob(encryptedKey)
                         .build();
                 
                 kmsClient = KmsClient.builder()
                         .region(Region.US_EAST_1)
                         .build();
                 
                 DecryptResponse decryptResponse = kmsClient.decrypt(decryptRequest);
                 
                 byte[] decryptKey = decryptResponse.plaintext().asByteArray();
                 

                 System.arraycopy(ciphertext, 0, ciphertextWithTag, 0, ciphertext.length);
                 System.arraycopy(tag, 0, ciphertextWithTag, ciphertext.length, tag.length);
                 
                 
                 // Perform AES-GCM decryption
                 Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
                 
                 SecretKeySpec keySpec = new SecretKeySpec(decryptKey, "AES");
                 
                 GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv); // 128-bit authentication tag

                 cipher.init(Cipher.DECRYPT_MODE, keySpec, gcmSpec);
                 
                 cipher.updateAAD(new byte[0]); // Empty AAD for compatibility
                 
                 byte[] decryptedBytes = cipher.doFinal(ciphertextWithTag);
                 
                 String decryptedMessage = new String(decryptedBytes, StandardCharsets.UTF_8);

                 
                 // Create a ResponseMessage object
                 Aes256DecryptResponseMessage responseMessage = new Aes256DecryptResponseMessage(
                 		decryptedMessage
                 );
                 String responseBody = objectMapper.writeValueAsString(responseMessage);

                 // Set success response
                 response.setStatusCode(200);
                 response.setBody(responseBody);
                 
                 return response;

            }
            catch (Exception e) {
            	
                // Handle any errors
                context.getLogger().log("Error decrypting AES-256: " + e.getMessage());
                
            	HashMap<String,String> rspErrorBody = new HashMap<>();
            	rspErrorBody.put("Error", "Error while decrypting AES-256: " + e.getMessage());

                // Set error response
                response.setStatusCode(500);
                response.setBody(rspErrorBody.toString());
                return response;
            }

            } catch (Exception e) {
        	
        	
            // Handle any errors
            context.getLogger().log("Error parsing request: " + e.getMessage());
            
        	HashMap<String,String> rspErrorBody = new HashMap<>();
        	rspErrorBody.put("Error", "Error while parsing request body: " + e.getMessage());

            // Set error response
            response.setStatusCode(500);
            response.setBody(rspErrorBody.toString());
            return response;
        }
    }
}
