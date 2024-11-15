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
import java.io.OutputStream;

public class Aes256DecryptProgram {
    private static final String KMS_KEY_ARN = System.getenv("AES_KMS_KEY_ARN");
    private static KmsClient kmsClient;

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        try {
            if (args.length != 1) {
                System.err.println("Usage: java Aes256DecryptProgram <message>");
                System.exit(1);
            }

            String requestJsonString = args[0];  // Get the message from the command line argument
            Aes256DecryptRequestMessage requestMessage = mapper.readValue(requestJsonString, Aes256DecryptRequestMessage.class);   

            // Decrypt the encrypted data key using KMS
            byte[] encryptedKeyBytes = Base64.getDecoder().decode(requestMessage.getEncryptedDataKey());
            // Decode IV, tag, and ciphertext
            byte[] iv = Base64.getDecoder().decode(requestMessage.getIv());
            byte[] tag = Base64.getDecoder().decode(requestMessage.getTag());
            byte[] ciphertext = Base64.getDecoder().decode(requestMessage.getEncryptedMessage());

            // Decrypt the encrypted key using KMS
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

            // Rebuild the encrypted data (ciphertext + tag)
            byte[] encryptedWithTag = new byte[ciphertext.length + tag.length];
            System.arraycopy(ciphertext, 0, encryptedWithTag, 0, ciphertext.length);
            System.arraycopy(tag, 0, encryptedWithTag, ciphertext.length, tag.length);

            // Perform AES-GCM decryption
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
            SecretKeySpec keySpec = new SecretKeySpec(decryptKey, "AES");
            GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv); // 96-bit authentication tag

            cipher.init(Cipher.DECRYPT_MODE, keySpec, gcmSpec);
            cipher.updateAAD(new byte[0]); // Empty AAD for compatibility

            // Decrypt the ciphertext
            byte[] decryptedBytes = cipher.doFinal(encryptedWithTag);

            // Convert decrypted bytes to string
            String decryptedMessage = new String(decryptedBytes, StandardCharsets.UTF_8);

            // Create a ResponseMessage object
            Aes256DecryptResponseMessage responseMessage = new Aes256DecryptResponseMessage(decryptedMessage);

            // Write to stdout
            OutputStream output = System.out;
            mapper.writeValue(output, responseMessage); 

        } catch (Exception e) {
            System.err.println("Error Decrypting AES256: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
