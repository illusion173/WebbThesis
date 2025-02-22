package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.nio.charset.StandardCharsets;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.kms.model.*;
import java.io.InputStream;
import java.io.OutputStream;

public class Ecc384SignProgram {
    private static final String KMS_KEY_ARN = System.getenv("ECC384_KMS_KEY_ARN");
    private static KmsClient kmsClient;
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        try  {
        
        if (args.length != 1) {
            System.err.println("Usage: java Sha384Program <message>");
            System.exit(1);
        }

        String requestJsonString = args[0];  // Get the message from the command line argument

        Ecc384SignRequestMessage request = mapper.readValue(requestJsonString, Ecc384SignRequestMessage.class);  
        
        String message = request.getMessage();
        
        // convert message to bytes
        SdkBytes messageBytes = SdkBytes.fromByteArray(message.getBytes(StandardCharsets.UTF_8));
			try {
				
				
				kmsClient = KmsClient.builder()
						.region(Region.US_EAST_1)
						.build();
				
				
				// Sign the message
				SignRequest signRequest = SignRequest.builder()
						.keyId(KMS_KEY_ARN)
						.message(messageBytes)
						.messageType("RAW")
						.signingAlgorithm(SigningAlgorithmSpec.ECDSA_SHA_384) // Use ECDSA_SHA_384 for P-384 curve
						.build();

				SignResponse signResponse = kmsClient.sign(signRequest);
			   
				// Get the signature
				byte[] signature = signResponse.signature().asByteArray();

				// Encode the signature to base64 for easier transport
				String signatureBase64 = Base64.getEncoder().encodeToString(signature);

				// Create a ResponseMessage object
				Ecc384SignResponseMessage responseMessage = new Ecc384SignResponseMessage(
						signatureBase64
				);
				
				// Write to stdout
				OutputStream output = System.out;
				mapper.writeValue(output, responseMessage); 

			}

				catch (Exception e) {
				System.err.println("Error: " + e.getMessage());
				e.printStackTrace();
				};
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
