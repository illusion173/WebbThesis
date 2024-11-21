package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.regions.Region;

import software.amazon.awssdk.services.kms.model.*;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

public class Ecc384VerifyProgram {
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

        Ecc384VerifyRequestMessage request = mapper.readValue(requestJsonString, Ecc384VerifyRequestMessage.class); 
        String signatureb64 = request.getSignature();
        String message = request.getMessage();
        byte[] signatureBytes = Base64.getDecoder().decode(signatureb64);
 
			try {
				
                kmsClient = KmsClient.builder()
                        .region(Region.US_EAST_1)
                        .build();
                

                // Verify the signature
                VerifyRequest verifyRequest = VerifyRequest.builder()
                        .keyId(KMS_KEY_ARN)
                        .message(SdkBytes.fromUtf8String(message))
                        .messageType("RAW")
                        .signature(SdkBytes.fromByteArray(signatureBytes))
                        .signingAlgorithm(SigningAlgorithmSpec.ECDSA_SHA_384)  // Use ECDSA_SHA_384 for P-384 curve
                        .build();

                VerifyResponse verifyResponse = kmsClient.verify(verifyRequest);

                // Check if the signature is valid
                boolean isValid = verifyResponse.signatureValid();
                // Create a ResponseMessage object
                Ecc384VerifyResponseMessage responseMessage = new Ecc384VerifyResponseMessage(
                		isValid
                );
				
				// Write to stdout
				OutputStream output = System.out;
				mapper.writeValue(output, responseMessage); 
				}
				catch (Exception e) {
				System.err.println("Error while Verifying ECC384: " + e.getMessage());
				e.printStackTrace();
				};
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
