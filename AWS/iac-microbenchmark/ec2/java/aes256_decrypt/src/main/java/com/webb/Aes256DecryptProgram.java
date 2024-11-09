package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.nio.charset.StandardCharsets;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.regions.Region;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import software.amazon.awssdk.services.kms.model.*;
import java.io.InputStream;
import java.io.OutputStream;
public class Aes256DecryptProgram {
    private static final String KMS_KEY_ARN = System.getenv("AES256_KMS_KEY_ARN");
    private static KmsClient kmsClient;
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        
        // Create KMS Client
        try  {

        	// Read from stdin
        	InputStream input = System.in;
        	Aes256DecryptRequestMessage requestMessage = mapper.readValue(input, Aes256DecryptRequestMessage.class);
        
            // Decrypt the encrypted key using KMS
            byte[] encryptedKeyBytes = Base64.getDecoder().decode(requestMessage.getEncrypted_key());
            // Decode IV, tag, and ciphertext
            byte[] iv = Base64.getDecoder().decode(requestMessage.getIv());
            byte[] tag = Base64.getDecoder().decode(requestMessage.getTag());
            byte[] ciphertext = Base64.getDecoder().decode(requestMessage.getCiphertext());
            byte[] ciphertextWithTag = new byte[ciphertext.length + tag.length];	

            try {
            	
            	SdkBytes encryptedKey = SdkBytes.fromByteArray(encryptedKeyBytes);

                DecryptRequest decryptRequest = DecryptRequest.builder()
                        .keyId(KMS_KEY_ARN)
                        .ciphertextBlob(encryptedKey)
                        .build();
                
                kmsClient = KmsClient.builder()
                        .region(Region.US_EAST_1)
                        .build();
                
                DecryptResponse decryptResponse = kmsClient.decrypt(decryptRequest);
                
                byte[] decryptKey = decryptResponse.plaintext().asByteArray();
                

                System.arraycopy(ciphertext, 0, ciphertextWithTag, 0, ciphertext.length);
                System.arraycopy(tag, 0, ciphertextWithTag, ciphertext.length, tag.length);
                
                
                // Perform AES-GCM decryption
                Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
                
                SecretKeySpec keySpec = new SecretKeySpec(decryptKey, "AES");
                
                GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv); // 128-bit authentication tag

                cipher.init(Cipher.DECRYPT_MODE, keySpec, gcmSpec);
                
                cipher.updateAAD(new byte[0]); // Empty AAD for compatibility
                
                byte[] decryptedBytes = cipher.doFinal(ciphertextWithTag);
                
                String decryptedMessage = new String(decryptedBytes, StandardCharsets.UTF_8);

                
                // Create a ResponseMessage object
                Aes256DecryptResponseMessage responseMessage = new Aes256DecryptResponseMessage(
                		decryptedMessage
                );	
                
                // Write to stdout
                OutputStream output = System.out;
                mapper.writeValue(output, responseMessage);	
            	
            } catch (Exception e)
            {
                System.err.println("Error Decrypting AES256: " + e.getMessage());
                e.printStackTrace();	
            }

        } catch (KmsException e) {
            System.err.println("Error reading from stdin: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
