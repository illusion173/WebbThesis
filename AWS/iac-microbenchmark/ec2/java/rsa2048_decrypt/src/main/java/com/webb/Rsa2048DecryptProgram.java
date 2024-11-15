package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.regions.Region;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

import software.amazon.awssdk.services.kms.model.*;
import java.io.OutputStream;

public class Rsa2048DecryptProgram {
    private static final String KMS_KEY_ARN = System.getenv("RSA2048_KMS_KEY_ARN");
    private static KmsClient kmsClient;
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        try  {
            // Read from stdin
            if (args.length != 1) {
                System.err.println("Usage: java Rsa2048DecryptProgram <message>");
                System.exit(1);
            }

            String requestJsonString = args[0];  // Get the message from the command line argument

            Rsa2048DecryptRequestMessage request = mapper.readValue(requestJsonString, Rsa2048DecryptRequestMessage.class);
            
            // Obtain Values, convert as needed.
            byte[] encryptedAesKey = Base64.getDecoder().decode(request.getEncryptedKey());
            
            byte[] iv = Base64.getDecoder().decode(request.getIv());
            
            byte[] ciphertext = Base64.getDecoder().decode(request.getCiphertext());
			
            try {
		        kmsClient = KmsClient.builder()
			            .region(Region.US_EAST_1)
			            .build();
		        
		        // Prepare the DecryptRequest
                DecryptRequest decryptRequest = DecryptRequest.builder()
                        .ciphertextBlob(SdkBytes.fromByteArray(encryptedAesKey))
                        .keyId(KMS_KEY_ARN)
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
	            
				// Write to stdout
				OutputStream output = System.out;
				mapper.writeValue(output, responseMessage); 
				}
			catch (Exception e) {
			System.err.println("Error while Decrypting RSA2048: " + e.getMessage());
			e.printStackTrace();
			};
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
