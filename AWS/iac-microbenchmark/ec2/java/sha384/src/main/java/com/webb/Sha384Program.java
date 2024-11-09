package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.nio.charset.StandardCharsets;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.kms.model.*;
import java.io.InputStream;
import java.io.OutputStream;

public class Sha384Program {
	
    private static final String KMS_KEY_ARN = System.getenv("SHA384_KMS_KEY_ARN");
    
    private static final String SIGN_ALGORITHM = "HMAC_SHA_384";
    
    private static KmsClient kmsClient; 
    
    public static void main(String[] args) throws Exception {

        ObjectMapper mapper = new ObjectMapper();

        // Read from stdin
        InputStream input = System.in;
        Sha384RequestMessage request = mapper.readValue(input, Sha384RequestMessage.class);
        String message = request.getMessage();
        
        // convert message to bytes
        SdkBytes messageBytes = SdkBytes.fromByteArray(message.getBytes(StandardCharsets.UTF_8));
 
     // Generate HMAC using kms
        try {
            // Initialize the KMS client
            kmsClient = KmsClient.builder()
                    .region(Region.US_EAST_1) // 
                    .credentialsProvider(DefaultCredentialsProvider.create())
                    .build();
            
            // Generate HMAC using KMS
            GenerateMacRequest generateMacRequest = GenerateMacRequest.builder()
                    .keyId(KMS_KEY_ARN)
                    .message(messageBytes)
                    .macAlgorithm(SIGN_ALGORITHM)
                    .build();


            GenerateMacResponse generateMacResponse = kmsClient.generateMac(generateMacRequest);
            
            
            byte[] mac = generateMacResponse.mac().asByteArray();

            // Base64 encode the signature for output
            String signature = Base64.getEncoder().encodeToString(mac);
            
            // Create a ResponseMessage object
            Sha384ResponseMessage responseMessage = new Sha384ResponseMessage(
            		signature
            );
            OutputStream output = System.out;
            mapper.writeValue(output, responseMessage);

        } catch (KmsException e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
