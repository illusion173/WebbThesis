package com.webb;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.util.HashMap;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.services.kms.model.SigningAlgorithmSpec;
import software.amazon.awssdk.services.kms.model.VerifyRequest;
import software.amazon.awssdk.services.kms.model.VerifyResponse;

public class LambdaHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    // Create an instance of ObjectMapper for JSON parsing and serialization
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private KmsClient kmsClient;

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
        
          // Create a response object
          APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent();
          HashMap<String,String> rspHeaders = new HashMap<>();
          rspHeaders.put("Access-Control-Allow-Origin", "*");
          rspHeaders.put("Content-Type", "application/json");
          response.setHeaders(rspHeaders);

        try {
        	
            // Get KMS key ARN from environment variables
            String Ecc384VerifyKmsKeyId = System.getenv("ECC384_KMS_KEY_ARN");
        	
            // Get the JSON string from the request body
            String body = request.getBody();
                    
            // Deserialize the request body into Sha384RequestMessage object
            Ecc384VerifyRequestMessage requestMessage = objectMapper.readValue(body, Ecc384VerifyRequestMessage.class);
          

            byte[] signature = Base64.getDecoder().decode(requestMessage.getSignature());
            byte[] message = Base64.getDecoder().decode(requestMessage.getMessage());
            
            
            try {
                kmsClient = KmsClient.builder()
                        .region(Region.US_EAST_1)
                        .build();
            	// Convert message to SdkBytes
                SdkBytes messageBytes = SdkBytes.fromByteArray(message);

                // Convert the signature to SdkBytes
                SdkBytes signatureBytes = SdkBytes.fromByteArray(signature);

                // Verify the signature
                VerifyRequest verifyRequest = VerifyRequest.builder()
                        .keyId(Ecc384VerifyKmsKeyId)
                        .message(messageBytes)
                        .messageType("RAW")
                        .signature(signatureBytes)
                        .signingAlgorithm(SigningAlgorithmSpec.ECDSA_SHA_384)  // Use ECDSA_SHA_384 for P-384 curve
                        .build();

                VerifyResponse verifyResponse = kmsClient.verify(verifyRequest);

                // Check if the signature is valid
                boolean isValid = verifyResponse.signatureValid();
                
                // Create a ResponseMessage object
                Ecc384VerifyResponseMessage responseMessage = new Ecc384VerifyResponseMessage(
                		isValid
                );
                String responseBody = objectMapper.writeValueAsString(responseMessage);

                // Set success response
                response.setStatusCode(200);
                response.setBody(responseBody);
                
                return response;
            	
            }	
	            catch (Exception e) {
	               	
	                // Handle any errors
	                context.getLogger().log("Error Verifying Signature ecc256: " + e.getMessage());
	                
	            	HashMap<String,String> rspErrorBody = new HashMap<>();
	            	rspErrorBody.put("Error", "Error while Verifying Signature ecc256: " + e.getMessage());
	
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
