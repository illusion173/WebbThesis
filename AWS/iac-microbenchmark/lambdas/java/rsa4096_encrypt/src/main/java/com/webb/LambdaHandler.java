package com.webb;

import java.util.Map;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.fasterxml.jackson.databind.ObjectMapper;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Base64;
public class LambdaHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    // Create an instance of ObjectMapper for JSON parsing and serialization
    private static final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
        context.getLogger().log("Received event: " + request);

        // Create a response object
        APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent();

        try {
            // Get the JSON string from the request body
            String body = request.getBody();
            context.getLogger().log("Request body: " + body);

            // Deserialize the request body into Rsa4096EncryptRequestMessage object
            Rsa4096EncryptRequestMessage requestMessage = objectMapper.readValue(body, Rsa4096EncryptRequestMessage.class);

            // Log the fields (message and sender)
            context.getLogger().log("Message: " + requestMessage.getMessage());
            context.getLogger().log("Sender: " + requestMessage.getSender());

            // Create a ResponseMessage object
            Rsa4096EncryptResponseMessage responseMessage = new Rsa4096EncryptResponseMessage(
                requestMessage.getMessage(),
                requestMessage.getSender(),
                "Success"
            );

            // Serialize ResponseMessage object to JSON
            String responseBody = objectMapper.writeValueAsString(responseMessage);

            // Set success response
            response.setStatusCode(200);
            response.setBody(responseBody);
            response.setHeaders(Map.of("Content-Type", "application/json"));
        } catch (Exception e) {
            // Handle any errors
            context.getLogger().log("Error parsing request: " + e.getMessage());

            // Create error response in JSON format
            Rsa4096EncryptResponseMessage errorResponse = new Rsa4096EncryptResponseMessage(null, null, "Error: " + e.getMessage());

            // Serialize the error response
            String responseBody = "";
            try {
                responseBody = objectMapper.writeValueAsString(errorResponse);
            } catch (Exception ex) {
                context.getLogger().log("Error serializing error response: " + ex.getMessage());
            }

            // Set error response
            response.setStatusCode(500);
            response.setBody(responseBody);
            response.setHeaders(Map.of("Content-Type", "application/json"));
        }

        return response;
    }
}