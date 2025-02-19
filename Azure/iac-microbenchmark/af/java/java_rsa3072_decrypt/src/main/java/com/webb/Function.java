package com.webb;

import com.microsoft.azure.functions.ExecutionContext;
import com.microsoft.azure.functions.HttpMethod;
import com.microsoft.azure.functions.HttpRequestMessage;
import com.microsoft.azure.functions.HttpResponseMessage;
import com.microsoft.azure.functions.HttpStatus;
import com.microsoft.azure.functions.annotation.AuthorizationLevel;
import com.microsoft.azure.functions.annotation.FunctionName;
import com.microsoft.azure.functions.annotation.HttpTrigger;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.KeyClientBuilder;
import com.azure.security.keyvault.keys.cryptography.*;
import com.azure.security.keyvault.keys.models.KeyVaultKey;
import com.azure.security.keyvault.keys.cryptography.models.DecryptResult;
import com.azure.security.keyvault.keys.cryptography.models.EncryptionAlgorithm;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import java.util.Optional;

/**
 * Azure Functions with HTTP Trigger.
 */
public class Function {

    private static final String KEY_VAULT_URL = System.getenv("AZURE_KEY_VAULT_URL");
    private static final String RSA3072_KEY_NAME = System.getenv("RSA3072_KEY_NAME");
    private static final ObjectMapper objectMapper = new ObjectMapper();

    
    @FunctionName("java_rsa3072_decrypt")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.POST},
                authLevel = AuthorizationLevel.ANONYMOUS)
                HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {
                try  {
                    String requestBody = request.getBody().orElse(null);

                    if (requestBody == null) {
                        return request.createResponseBuilder(HttpStatus.BAD_REQUEST).body("Please pass a request body").build();
                    }


                    rsa3072_decryptRequestMessage rsa3072_decryptrequest = objectMapper.readValue(requestBody, rsa3072_decryptRequestMessage.class);


                    byte[] ivBytes = Base64.getDecoder().decode(rsa3072_decryptrequest.getiv());
                    byte[] cipherTextBytes = Base64.getDecoder().decode(rsa3072_decryptrequest.getciphertext());
                    byte[] encryptedAesKeyBytes = Base64.getDecoder().decode(rsa3072_decryptrequest.getencrypted_aes_key());

                    
                    DefaultAzureCredential creds = new DefaultAzureCredentialBuilder().build();

                    
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

                    // Process the request and create response object
                    rsa3072_decryptResponseMessage responseObj = new rsa3072_decryptResponseMessage(plaintextMessage);

                    // Convert response object to JSON string
                    String jsonResponse = objectMapper.writeValueAsString(responseObj);

                    return request.createResponseBuilder(HttpStatus.OK).body(jsonResponse).build();
                } catch (Exception e) {
                    return request.createResponseBuilder(HttpStatus.BAD_REQUEST).body("Error: " + e.getMessage()).build();
                }
    }

}
