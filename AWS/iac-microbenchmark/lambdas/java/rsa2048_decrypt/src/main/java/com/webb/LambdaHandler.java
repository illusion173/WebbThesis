package com.webb;


import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.util.HashMap;

import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.services.kms.model.DecryptRequest;
import software.amazon.awssdk.services.kms.model.DecryptResponse;
import software.amazon.awssdk.regions.Region;

import javax.crypto.Cipher;

import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

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
            String Rsa2048DecryptKmsKeyId = System.getenv("RSA2048_KMS_KEY_ARN");
        	
            // Get the JSON string from the request body
            String body = request.getBody();
                    
            // Deserialize the request body into RSA2048 RequestMessage object

            Rsa2048DecryptRequestMessage requestMessage = objectMapper.readValue(body, Rsa2048DecryptRequestMessage.class);

            // Obtain Values, convert as needed.
            byte[] encryptedAesKey = Base64.getDecoder().decode(requestMessage.getEncryptedAesKey());
            
            byte[] iv = Base64.getDecoder().decode(requestMessage.getIv());
            
            byte[] ciphertext = Base64.getDecoder().decode(requestMessage.getCiphertext());
            
		    try {
		        kmsClient = KmsClient.builder()
			            .region(Region.US_EAST_1)
			            .build();
		        
		        // Prepare the DecryptRequest
                DecryptRequest decryptRequest = DecryptRequest.builder()
                        .ciphertextBlob(SdkBytes.fromByteArray(encryptedAesKey))
                        .keyId(Rsa2048DecryptKmsKeyId)
                        .encryptionAlgorithm(software.amazon.awssdk.services.kms.model.EncryptionAlgorithmSpec.RSAES_OAEP_SHA_256)
                        .build();
		        
                // Call AWS KMS to decrypt the AES key
                DecryptResponse decryptResponse = kmsClient.decrypt(decryptRequest);

                // Get the decrypted AES key (plaintext AES key)
                byte[] aesKey = decryptResponse.plaintext().asByteArray();

                // Step 2: Decrypt the message using the AES-CTR cipher and decrypted AES key
                Cipher cipher = Cipher.getInstance("AES/CTR/NoPadding");

                // Recreate the SecretKeySpec and IvParameterSpec from the decrypted AES key and IV
                SecretKeySpec secretKeySpec = new SecretKeySpec(aesKey, "AES");
                IvParameterSpec ivParameterSpec = new IvParameterSpec(iv);

                // Initialize cipher in DECRYPT mode
                cipher.init(Cipher.DECRYPT_MODE, secretKeySpec, ivParameterSpec);

                // Decrypt the ciphertext
                byte[] decryptedMessageBytes = cipher.doFinal(ciphertext);

                // Convert decrypted bytes to a string (original message)
                String plaintextMessage = new String(decryptedMessageBytes, "UTF-8");
		 
	            Rsa2048DecryptResponseMessage responseMessage = new Rsa2048DecryptResponseMessage(
	            		plaintextMessage
	            );
	         	            
	            String responseBody = objectMapper.writeValueAsString(responseMessage);
	                        
	            // Set success response
	            response.setStatusCode(200);
	            response.setBody(responseBody);
	            
	            
	            return response;
		        
		    }
		        catch (Exception e) {

		        // Handle any errors
		        context.getLogger().log("Error Decrypting RSA 2048: " + e.getMessage());
		        
		    	HashMap<String,String> rspErrorBody = new HashMap<>();
		    	rspErrorBody.put("Error", "Error while Decrypting RSA 2048: " + e.getMessage());
		
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
