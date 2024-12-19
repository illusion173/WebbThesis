package com.webb;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.util.HashMap;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.services.kms.model.GenerateDataKeyRequest;
import software.amazon.awssdk.services.kms.model.GenerateDataKeyResponse;
import software.amazon.awssdk.regions.Region;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import java.util.Arrays;



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
            String Aes256EncryptKmsKeyId = System.getenv("AES256_KMS_KEY_ARN");
        	
            // Get the JSON string from the request body
            String body = request.getBody();
                    
            // Deserialize the request body into Sha256RequestMessage object
            Aes256EncryptRequestMessage requestMessage = objectMapper.readValue(body, Aes256EncryptRequestMessage.class);


            String message = requestMessage.getMessage();
            byte[] messageBytes = message.getBytes();
                       
            try {

        		kmsClient = KmsClient.builder()
        			        .region(Region.US_EAST_1)
        			        .build();
                
                // Step 1: Generate a Data Key
                GenerateDataKeyRequest dataKeyRequest = GenerateDataKeyRequest.builder()
                        .keyId(Aes256EncryptKmsKeyId) // The KMS Key ID
                        .keySpec("AES_256") // Specifying the key spec as AES_256
                        .build(); 
                
                
                GenerateDataKeyResponse dataKeyResponse = kmsClient.generateDataKey(dataKeyRequest);
                
                // Step 2: Extract the Plaintext (unencrypted) Data Key
                SdkBytes plaintextDataKey = dataKeyResponse.plaintext(); // The unencrypted key
                if (plaintextDataKey == null) {
                    throw new RuntimeException("No plaintext data key returned");
                }

                byte[] plaintextDataKeyBytes = plaintextDataKey.asByteArray(); // Convert to byte array

                // Step 3: Extract the Encrypted Data Key
                SdkBytes encryptedDataKey = dataKeyResponse.ciphertextBlob(); // The encrypted key
                if (encryptedDataKey == null) {
                    throw new RuntimeException("No encrypted data key returned");
                }

                byte[] encryptedDataKeyBytes = encryptedDataKey.asByteArray(); // Convert to byte array

                // Step 4: Create IV
                byte[] iv = new byte[12]; // 
                
                SecureRandom secureRandom = new SecureRandom();
                
                secureRandom.nextBytes(iv);
                
                
                Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
                
                SecretKeySpec keySpec = new SecretKeySpec(plaintextDataKeyBytes, "AES");

                GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);

                cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec);
                
                
                // Step 5: Encrypt the message (this will include generating the tag)
                byte[] ciphertext = cipher.doFinal(messageBytes);
                
                // The tag is automatically appended to the ciphertext in GCM mode, so:
                byte[] tag = Arrays.copyOfRange(ciphertext, ciphertext.length - 16, ciphertext.length);
                byte[] encryptedData = Arrays.copyOfRange(ciphertext, 0, ciphertext.length - 16);
                
                String ivb64 = Base64.getEncoder().encodeToString(iv);
                String tagb64 = Base64.getEncoder().encodeToString(tag);
                String cipherTextb64 = Base64.getEncoder().encodeToString(encryptedData);
                String encrypted_aes_keyb64 = Base64.getEncoder().encodeToString(encryptedDataKeyBytes);
                
                // Create a ResponseMessage object
                Aes256EncryptResponseMessage responseMessage = new Aes256EncryptResponseMessage(
                		cipherTextb64,
                		ivb64,
                		tagb64,
                		encrypted_aes_keyb64
                );
                
                String responseBody = objectMapper.writeValueAsString(responseMessage);

                // Set success response
                response.setStatusCode(200);
                response.setBody(responseBody);
                
                return response;

           }
           catch (Exception e) {
           	
               // Handle any errors
               context.getLogger().log("Error encrypting AES-256: " + e.getMessage());
               
           	HashMap<String,String> rspErrorBody = new HashMap<>();
           	rspErrorBody.put("Error", "Error while encrypting AES-256: " + e.getMessage());

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
