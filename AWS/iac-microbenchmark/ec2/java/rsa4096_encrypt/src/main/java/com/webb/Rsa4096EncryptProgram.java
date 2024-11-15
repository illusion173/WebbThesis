package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.regions.Region;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import software.amazon.awssdk.services.kms.model.*;
import java.io.InputStream;
import java.io.OutputStream;

public class Rsa4096EncryptProgram {
    private static final String KMS_KEY_ARN = System.getenv("RSA4096_KMS_KEY_ARN");
    private static KmsClient kmsClient;
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        try  {
        // Read from stdin
        if (args.length != 1) {
            System.err.println("Usage: java Rsa4096EncryptProgram <message>");
            System.exit(1);
        }

        String requestJsonString = args[0];  // Get the message from the command line argument

        Rsa4096EncryptRequestMessage request = mapper.readValue(requestJsonString, Rsa4096EncryptRequestMessage.class);
        
        String message = request.getMessage();
        
        try {
        	
            // Generate AES key and IV
            byte[] aesKey = new byte[32]; // 32 bytes for AES-256
            byte[] iv = new byte[16]; // 16 bytes for IV
            SecureRandom secureRandom = new SecureRandom();

            secureRandom.nextBytes(aesKey);
            secureRandom.nextBytes(iv);
            
            // Encrypt the message using AES-CTR
            Cipher cipher = Cipher.getInstance("AES/CTR/NoPadding");
            
            SecretKeySpec secretKeySpec = new SecretKeySpec(aesKey, "AES");
            
            IvParameterSpec ivParameterSpec = new IvParameterSpec(iv);
            
            cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec, ivParameterSpec); 
            
            byte[] ciphertext = cipher.doFinal(message.getBytes("UTF-8"));
                            
		    kmsClient = KmsClient.builder()
		            .region(Region.US_EAST_1)
		            .build();
                            
           EncryptRequest encryptRequest = EncryptRequest.builder()
                    .keyId(KMS_KEY_ARN)
                    .plaintext(SdkBytes.fromByteArray(aesKey))
                    .encryptionAlgorithm(software.amazon.awssdk.services.kms.model.EncryptionAlgorithmSpec.RSAES_OAEP_SHA_256)
                    .build();

            EncryptResponse encryptResponse = kmsClient.encrypt(encryptRequest);
            
            byte[] encryptedAesKey = encryptResponse.ciphertextBlob().asByteArray();

            String encodedCiphertext = Base64.getEncoder().encodeToString(ciphertext);
            
            String encodedIv = Base64.getEncoder().encodeToString(iv);
            
            String encodedEncryptedAesKey = Base64.getEncoder().encodeToString(encryptedAesKey);
            

            // Return the response
            Rsa4096EncryptResponseMessage rsaResponse = new Rsa4096EncryptResponseMessage(encodedCiphertext, encodedIv, encodedEncryptedAesKey);
			
			// Write to stdout
			OutputStream output = System.out;
			mapper.writeValue(output, rsaResponse); 
				}
			catch (Exception e) {
			System.err.println("Error while Encrypting RSA4096: " + e.getMessage());
			e.printStackTrace();
			};
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
