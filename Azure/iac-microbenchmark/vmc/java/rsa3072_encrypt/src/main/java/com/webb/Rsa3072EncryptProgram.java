package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.security.SecureRandom;
import java.io.OutputStream;
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.KeyClientBuilder;
import com.azure.security.keyvault.keys.cryptography.*;
import com.azure.security.keyvault.keys.models.KeyVaultKey;
import com.azure.security.keyvault.keys.cryptography.models.EncryptResult;
import com.azure.security.keyvault.keys.cryptography.models.EncryptionAlgorithm;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import com.azure.identity.AzureCliCredential;
import com.azure.identity.AzureCliCredentialBuilder;
public class Rsa3072EncryptProgram {
    private static final String KEY_VAULT_URL = System.getenv("AZURE_KEY_VAULT_URL");
    private static final String RSA3072_KEY_NAME = System.getenv("RSA3072_KEY_NAME");

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        try  {

            if (args.length != 1) {
                System.err.println("Usage: java Rsa3072Encrypt <message>");
                System.exit(1);
            }

        String requestJsonString = args[0];  // Get the message from the command line argument

        Rsa3072EncryptRequestMessage request = mapper.readValue(requestJsonString, Rsa3072EncryptRequestMessage.class);
        byte[] messageBytes = request.getmessage().getBytes();

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
        
        byte[] ciphertext = cipher.doFinal(messageBytes);
        
        AzureCliCredential creds = new AzureCliCredentialBuilder().build();
        
        KeyClient keyClient = new KeyClientBuilder().credential(creds).vaultUrl(KEY_VAULT_URL).buildClient();
        
        KeyVaultKey key = keyClient.getKey(RSA3072_KEY_NAME);
        CryptographyClient cryptoClient = new CryptographyClientBuilder()
        	    .keyIdentifier(key.getId())
        	    .credential(creds)
        	    .buildClient(); 

        EncryptResult encryptResponse = cryptoClient.encrypt(EncryptionAlgorithm.RSA_OAEP_256, aesKey);
        
        String ivBase64 = Base64.getEncoder().encodeToString(iv);
        String cipherText = Base64.getEncoder().encodeToString(ciphertext);

        String encryptedAesKeyBase64 = Base64.getEncoder().encodeToString(encryptResponse.getCipherText());
        
        Rsa3072EncryptResponseMessage response = new Rsa3072EncryptResponseMessage(ivBase64, cipherText, encryptedAesKeyBase64);
        
        // Write to stdout
        OutputStream output = System.out;
        mapper.writeValue(output, response);
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}


