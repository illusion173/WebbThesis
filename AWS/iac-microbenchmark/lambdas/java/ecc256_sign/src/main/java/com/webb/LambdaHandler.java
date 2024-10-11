package com.webb;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.util.HashMap;
import java.nio.charset.StandardCharsets;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.services.kms.model.SignResponse;
import software.amazon.awssdk.services.kms.model.SignRequest;
import software.amazon.awssdk.services.kms.model.SigningAlgorithmSpec;
import software.amazon.awssdk.regions.Region;

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
            String Ecc256SignKmsKeyId = System.getenv("ECC256_KMS_KEY_ARN");
        	
            // Get the JSON string from the request body
            String body = request.getBody();
                    
            // Deserialize the request body into Sha256RequestMessage object

            //
            Ecc256SignRequestMessage requestMessage = objectMapper.readValue(body, Ecc256SignRequestMessage.class);

            String message = requestMessage.getMessage();
            
            // convert message to bytes
            SdkBytes messageBytes = SdkBytes.fromByteArray(message.getBytes(StandardCharsets.UTF_8));
            
            try {
            	
            	
                kmsClient = KmsClient.builder()
                        .region(Region.US_EAST_1)
                        .build();
            	
                
                // Sign the message
                SignRequest signRequest = SignRequest.builder()
                        .keyId(Ecc256SignKmsKeyId)
                        .message(messageBytes)
                        .messageType("RAW")
                        .signingAlgorithm(SigningAlgorithmSpec.ECDSA_SHA_256) // Use ECDSA_SHA_384 for P-384 curve
                        .build();

                SignResponse signResponse = kmsClient.sign(signRequest);
               
                // Get the signature
                byte[] signature = signResponse.signature().asByteArray();

                // Encode the signature to base64 for easier transport
                String signatureBase64 = Base64.getEncoder().encodeToString(signature);

                // Create a ResponseMessage object
                Ecc256SignResponseMessage responseMessage = new Ecc256SignResponseMessage(
                		signatureBase64
                );
                
                String responseBody = objectMapper.writeValueAsString(responseMessage);

                // Set success response
                response.setStatusCode(200);
                response.setBody(responseBody);
                
                return response;    
            }

            	catch (Exception e) {
        	
	        	
	            // Handle any errors
	            context.getLogger().log("Error Signing ECC256: " + e.getMessage());
	            
	        	HashMap<String,String> rspErrorBody = new HashMap<>();
	        	rspErrorBody.put("Error", "Error while Signing ECC256: " + e.getMessage());
	
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
