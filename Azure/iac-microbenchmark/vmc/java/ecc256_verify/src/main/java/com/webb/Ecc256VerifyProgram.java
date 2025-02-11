package com.webb;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.io.OutputStream;
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.KeyClientBuilder;
import com.azure.security.keyvault.keys.cryptography.*;
import com.azure.security.keyvault.keys.models.KeyVaultKey;
import com.azure.security.keyvault.keys.cryptography.models.SignatureAlgorithm;
import com.azure.security.keyvault.keys.cryptography.models.VerifyResult;
import com.azure.identity.AzureCliCredential;
import com.azure.identity.AzureCliCredentialBuilder;
public class Ecc256VerifyProgram {
    private static final String KEY_VAULT_URL = System.getenv("AZURE_KEY_VAULT_URL");
    private static final String ECC256_KEY_NAME = System.getenv("ECC256_KEY_NAME");

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        try  {

            if (args.length != 1) {
                System.err.println("Usage: java Ecc256Verify <message>");
                System.exit(1);
            }

        String requestJsonString = args[0];  // Get the message from the command line argument

        Ecc256VerifyRequestMessage request = mapper.readValue(requestJsonString, Ecc256VerifyRequestMessage.class);
        byte[] messageDigestBytes = hexStringToByteArray(request.getmessage_digest());
        byte[] signatureBytes = Base64.getUrlDecoder().decode(request.getsignature());
 
        
        AzureCliCredential creds = new AzureCliCredentialBuilder().build();

        
        KeyClient keyClient = new KeyClientBuilder().credential(creds).vaultUrl(KEY_VAULT_URL).buildClient();
        
        KeyVaultKey key = keyClient.getKey(ECC256_KEY_NAME);
        CryptographyClient cryptoClient = new CryptographyClientBuilder()
        	    .keyIdentifier(key.getId())
        	    .credential(creds)
        	    .buildClient();
        
        VerifyResult verifyResult = cryptoClient.verify(SignatureAlgorithm.ES256, messageDigestBytes,signatureBytes );
        
        Ecc256VerifyResponseMessage response = new Ecc256VerifyResponseMessage(verifyResult.isValid());
        // Write to stdout
        OutputStream output = System.out;
        mapper.writeValue(output, response);
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
    private static byte[] hexStringToByteArray(String s) {
        int len = s.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4)
                    + Character.digit(s.charAt(i + 1), 16));
        }
        return data;
    }
}


