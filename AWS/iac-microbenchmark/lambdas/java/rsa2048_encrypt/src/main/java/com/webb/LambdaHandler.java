package com.webb;


import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.security.SecureRandom;
import java.util.Base64;
import java.util.HashMap;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.services.kms.model.EncryptRequest;
import software.amazon.awssdk.services.kms.model.EncryptResponse;
import com.amazonaws.services.lambda.runtime.Context;

public class LambdaHandler implements RequestHandler<APIGatewayV2HTTPEvent, APIGatewayV2HTTPResponse> {

    // Create an instance of ObjectMapper for JSON parsing and serialization
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private KmsClient kmsClient;

    @Override
    public APIGatewayV2HTTPResponse handleRequest(APIGatewayV2HTTPEvent request, Context context) {

          // Create a response object
          APIGatewayV2HTTPResponse response = new APIGatewayV2HTTPResponse();
          HashMap<String,String> rspHeaders = new HashMap<>();
          rspHeaders.put("Access-Control-Allow-Origin", "*");
          rspHeaders.put("Content-Type", "application/json");
          response.setHeaders(rspHeaders);

        try {
        	
            // Get KMS key ARN from environment variables
            String Rsa2048EncryptKmsKeyId = System.getenv("RSA2048_KMS_KEY_ARN");
        	
            // Get the JSON string from the request body
            String body = request.getBody();
                    
            // Deserialize the request body into Sha256RequestMessage object

            Rsa2048EncryptRequestMessage requestMessage = objectMapper.readValue(body, Rsa2048EncryptRequestMessage.class);


            String message = requestMessage.getMessage();
            

            
            try {
            	
                // Generate AES key and IV
                byte[] aesKey = new byte[32]; // 32 bytes for AES-256
                byte[] iv = new byte[16]; // 16 bytes for IV
                SecureRandom secureRandom = new SecureRandom();

                secureRandom.nextBytes(aesKey);
                secureRandom.nextBytes(iv);
                
                // Encrypt the message using AES-CTR
                Cipher cipher = Cipher.getInstance("AES/CTR/NoPadding");
                
                SecretKeySpec secretKeySpec = new SecretKeySpec(aesKey, "AES");
                
                IvParameterSpec ivParameterSpec = new IvParameterSpec(iv);
                
                cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec, ivParameterSpec); 
                
                byte[] ciphertext = cipher.doFinal(message.getBytes("UTF-8"));
                                
			    kmsClient = KmsClient.builder()
			            .region(Region.US_EAST_1)
			            .build();
                                
               EncryptRequest encryptRequest = EncryptRequest.builder()
                        .keyId(Rsa2048EncryptKmsKeyId)
                        .plaintext(SdkBytes.fromByteArray(aesKey))
                        .encryptionAlgorithm(software.amazon.awssdk.services.kms.model.EncryptionAlgorithmSpec.RSAES_OAEP_SHA_256)
                        .build();

                EncryptResponse encryptResponse = kmsClient.encrypt(encryptRequest);
                
                byte[] encryptedAesKey = encryptResponse.ciphertextBlob().asByteArray();

                String encodedCiphertext = Base64.getEncoder().encodeToString(ciphertext);
                
                String encodedIv = Base64.getEncoder().encodeToString(iv);
                
                String encodedEncryptedAesKey = Base64.getEncoder().encodeToString(encryptedAesKey);
                

                // Return the response
                Rsa2048EncryptResponseMessage rsaResponse = new Rsa2048EncryptResponseMessage(encodedCiphertext, encodedIv, encodedEncryptedAesKey);

                String responseBody = objectMapper.writeValueAsString(rsaResponse);

                // Set success response
                response.setStatusCode(200);
                response.setBody(responseBody);
                
                
                return response;
            }
            catch (Exception e) {
            	
            	
                // Handle any errors
                context.getLogger().log("Error encrypting RSA2048: " + e.getMessage());
                
            	HashMap<String,String> rspErrorBody = new HashMap<>();
            	rspErrorBody.put("Error", "Error while encrypting RSA2048: " + e.getMessage());

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
