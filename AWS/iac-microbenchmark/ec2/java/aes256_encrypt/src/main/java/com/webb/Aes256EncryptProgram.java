package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Arrays;
import java.util.Base64;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.regions.Region;

import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

import java.security.SecureRandom;
import software.amazon.awssdk.services.kms.model.*;
import java.io.OutputStream;

public class Aes256EncryptProgram {
    private static final String KMS_KEY_ARN = System.getenv("AES_KMS_KEY_ARN");
    private static KmsClient kmsClient;
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        // Read from stdin
        try {
        
        if (args.length != 1) {
            System.err.println("Usage: java AES256 <message>");
            System.exit(1);
        }

        String requestJsonString = args[0];  // Get the message from the command line argument

        Aes256EncryptRequestMessage request = mapper.readValue(requestJsonString, Aes256EncryptRequestMessage.class);   
        
        
        String message = request.getMessage();
        byte[] messageBytes = message.getBytes();
        
		kmsClient = KmsClient.builder()
			        .region(Region.US_EAST_1)
			        .build();
        
        // Step 1: Generate a Data Key
        GenerateDataKeyRequest dataKeyRequest = GenerateDataKeyRequest.builder()
                .keyId(KMS_KEY_ARN) // The KMS Key ID
                .keySpec("AES_256") // Specifying the key spec as AES_256
                .build(); 
        
        
        GenerateDataKeyResponse dataKeyResponse = kmsClient.generateDataKey(dataKeyRequest);
        
        // Step 2: Extract the Plaintext (unencrypted) Data Key
        SdkBytes plaintextDataKey = dataKeyResponse.plaintext(); // The unencrypted key
        if (plaintextDataKey == null) {
            throw new RuntimeException("No plaintext data key returned");
        }

        byte[] plaintextDataKeyBytes = plaintextDataKey.asByteArray(); // Convert to byte array

        // Step 3: Extract the Encrypted Data Key
        SdkBytes encryptedDataKey = dataKeyResponse.ciphertextBlob(); // The encrypted key
        if (encryptedDataKey == null) {
            throw new RuntimeException("No encrypted data key returned");
        }

        byte[] encryptedDataKeyBytes = encryptedDataKey.asByteArray(); // Convert to byte array

        // Step 4: Create IV
        byte[] iv = new byte[12]; // 
        
        SecureRandom secureRandom = new SecureRandom();
        
        secureRandom.nextBytes(iv);
        
        
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        
        SecretKeySpec keySpec = new SecretKeySpec(plaintextDataKeyBytes, "AES");

        // GCM uses 128-bit tags, and we pass in 96-bit (12-byte) tag length
        GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);

        cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec);
        
        
        // Step 5: Encrypt the message (this will include generating the tag)
        byte[] ciphertext = cipher.doFinal(messageBytes);
        
        // The tag is automatically appended to the ciphertext in GCM mode, so:
        byte[] tag = Arrays.copyOfRange(ciphertext, ciphertext.length - 16, ciphertext.length);
        byte[] encryptedData = Arrays.copyOfRange(ciphertext, 0, ciphertext.length - 16);
        
        String ivb64 = Base64.getEncoder().encodeToString(iv);
        String tagb64 = Base64.getEncoder().encodeToString(tag);
        String cipherTextb64 = Base64.getEncoder().encodeToString(encryptedData);
        String encrypted_aes_keyb64 = Base64.getEncoder().encodeToString(encryptedDataKeyBytes);
        
        // Create a ResponseMessage object
        Aes256EncryptResponseMessage responseMessage = new Aes256EncryptResponseMessage(
        		cipherTextb64,
        		ivb64,
        		tagb64,
        		encrypted_aes_keyb64
        ); 

		// Write to stdout
		OutputStream output = System.out;
		mapper.writeValue(output, responseMessage);
    
    	} catch (Exception e) {
    	
        System.err.println("Error AES_256_Java: " + e.getMessage());
        e.printStackTrace();    	
    	
}      

    }
}
