package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.regions.Region;

import software.amazon.awssdk.services.kms.model.*;
import java.io.InputStream;
import java.io.OutputStream;

public class Ecc384VerifyProgram {
    private static final String KMS_KEY_ARN = System.getenv("ECC384_KMS_KEY_ARN");
    
    private static KmsClient kmsClient;
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        try  {
        // Read from stdin
        InputStream input = System.in;
        Ecc384VerifyRequestMessage request = mapper.readValue(input, Ecc384VerifyRequestMessage.class);
        
        // convert message to bytes
        byte[] signatureByteArr = Base64.getDecoder().decode(request.getSignature());
        byte[] messageByteArr = Base64.getDecoder().decode(request.getMessage()); 
        
			try {
				
                kmsClient = KmsClient.builder()
                        .region(Region.US_EAST_1)
                        .build();
                
            	// Convert message to SdkBytes
                SdkBytes messageBytes = SdkBytes.fromByteArray(signatureByteArr);

                // Convert the signature to SdkBytes
                SdkBytes signatureBytes = SdkBytes.fromByteArray(messageByteArr);

                // Verify the signature
                VerifyRequest verifyRequest = VerifyRequest.builder()
                        .keyId(KMS_KEY_ARN)
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
