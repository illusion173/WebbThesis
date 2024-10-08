package com.webb;

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
import software.amazon.awssdk.services.kms.model.GenerateMacRequest;
import software.amazon.awssdk.services.kms.model.GenerateMacResponse;
import software.amazon.awssdk.regions.Region;

public class LambdaHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    // Create an instance of ObjectMapper for JSON parsing and serialization
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final String SIGN_ALGORITHM = "HMAC_SHA_256";
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
            String shaKmsKeyId = System.getenv("SHA256_KMS_KEY_ARN");
        	
            // Get the JSON string from the request body
            String body = request.getBody();
                    
            // Deserialize the request body into Sha256RequestMessage object
            Sha256RequestMessage requestMessage = objectMapper.readValue(body, Sha256RequestMessage.class);
            
            String message = requestMessage.getMessage();
            
            // convert message to bytes
            SdkBytes messageBytes = SdkBytes.fromByteArray(message.getBytes(StandardCharsets.UTF_8));
            
            // Generate HMAC using kms
            try {
                // Initialize the KMS client
                this.kmsClient = KmsClient.builder()
                        .region(Region.US_EAST_1) // 
                        .credentialsProvider(DefaultCredentialsProvider.create())
                        .build();
                
                // Generate HMAC using KMS
                GenerateMacRequest generateMacRequest = GenerateMacRequest.builder()
                        .keyId(shaKmsKeyId)
                        .message(messageBytes)
                        .macAlgorithm(SIGN_ALGORITHM)
                        .build();


                GenerateMacResponse generateMacResponse = kmsClient.generateMac(generateMacRequest);
                
                
                byte[] mac = generateMacResponse.mac().asByteArray();

                // Base64 encode the signature for output
                String signature = Base64.getEncoder().encodeToString(mac);
                
                // Create a ResponseMessage object
                Sha256ResponseMessage responseMessage = new Sha256ResponseMessage(
                		signature
                );

                // Serialize ResponseMessage object to JSON
                String responseBody = objectMapper.writeValueAsString(responseMessage);

                // Set success response
                response.setStatusCode(200);
                response.setBody(responseBody);
                
                
                return response;

            } catch (Exception e) {
            	
            	
                context.getLogger().log("Error generating MAC:  " + e.getMessage());
                
            	HashMap<String,String> rspErrorBody = new HashMap<>();
            	rspErrorBody.put("Error", "Error generating MAC: " + e.getMessage());

                // Set error response
                response.setStatusCode(500);
                response.setBody(rspErrorBody.toString());
               
                // Return error response
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
