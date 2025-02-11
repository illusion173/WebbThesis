package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.io.OutputStream;

import com.azure.identity.AzureCliCredential;
import com.azure.identity.AzureCliCredentialBuilder;
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.KeyClientBuilder;
import com.azure.security.keyvault.keys.cryptography.*;
import com.azure.security.keyvault.keys.models.KeyVaultKey;
import com.azure.security.keyvault.keys.cryptography.models.DecryptResult;
import com.azure.security.keyvault.keys.cryptography.models.EncryptionAlgorithm;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class Rsa3072DecryptProgram {
    private static final String KEY_VAULT_URL = System.getenv("AZURE_KEY_VAULT_URL");
    private static final String RSA3072_KEY_NAME = System.getenv("RSA3072_KEY_NAME");

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        try  {

            if (args.length != 1) {
                System.err.println("Usage: java Rsa3072Decrypt <message>");
                System.exit(1);
            }

        String requestJsonString = args[0];  // Get the message from the command line argument

        Rsa3072DecryptRequestMessage request = mapper.readValue(requestJsonString, Rsa3072DecryptRequestMessage.class);
        
        byte[] ivBytes = Base64.getDecoder().decode(request.getiv());
        byte[] cipherTextBytes = Base64.getDecoder().decode(request.getciphertext());
        byte[] encryptedAesKeyBytes = Base64.getDecoder().decode(request.getencrypted_aes_key());

        AzureCliCredential creds = new AzureCliCredentialBuilder().build();

        KeyClient keyClient = new KeyClientBuilder().credential(creds).vaultUrl(KEY_VAULT_URL).buildClient();
        
        KeyVaultKey key = keyClient.getKey(RSA3072_KEY_NAME);
        CryptographyClient cryptoClient = new CryptographyClientBuilder()
        	    .keyIdentifier(key.getId())
        	    .credential(creds)
        	    .buildClient(); 
        //Step 1: Get decrypted Key
        DecryptResult decryptResponse = cryptoClient.decrypt(EncryptionAlgorithm.RSA_OAEP_256, encryptedAesKeyBytes);
        byte[] aesKey = decryptResponse.getPlainText();
        
        
        // Step 2: Decrypt the message using the AES-CTR cipher and decrypted AES key
        Cipher cipher = Cipher.getInstance("AES/CTR/NoPadding");

        // Recreate the SecretKeySpec and IvParameterSpec from the decrypted AES key and IV
        SecretKeySpec secretKeySpec = new SecretKeySpec(aesKey, "AES");
        IvParameterSpec ivParameterSpec = new IvParameterSpec(ivBytes);

        // Initialize cipher in DECRYPT mode
        cipher.init(Cipher.DECRYPT_MODE, secretKeySpec, ivParameterSpec);

        // Decrypt the ciphertext
        byte[] decryptedMessageBytes = cipher.doFinal(cipherTextBytes);

        // Convert decrypted bytes to a string (original message)
        String plaintextMessage = new String(decryptedMessageBytes, "UTF-8");
         
        
        Rsa3072DecryptResponseMessage response = new Rsa3072DecryptResponseMessage(plaintextMessage);

        // Write to stdout
        OutputStream output = System.out;
        mapper.writeValue(output, response);
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}


