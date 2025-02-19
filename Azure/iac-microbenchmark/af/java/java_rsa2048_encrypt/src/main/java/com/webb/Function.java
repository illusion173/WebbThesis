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
import java.security.SecureRandom;
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.KeyClientBuilder;
import com.azure.security.keyvault.keys.cryptography.*;
import com.azure.security.keyvault.keys.models.KeyVaultKey;
import com.azure.security.keyvault.keys.cryptography.models.EncryptResult;
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
    private static final String RSA2048_KEY_NAME = System.getenv("RSA2048_KEY_NAME");
    private static final ObjectMapper objectMapper = new ObjectMapper();

    
    @FunctionName("java_rsa2048_encrypt")
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


                    rsa2048_encryptRequestMessage rsa2048_encryptrequest = objectMapper.readValue(requestBody, rsa2048_encryptRequestMessage.class);

                    byte[] messageBytes = rsa2048_encryptrequest.getmessage().getBytes();

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
                    
                    DefaultAzureCredential creds = new DefaultAzureCredentialBuilder().build();

                    
                    KeyClient keyClient = new KeyClientBuilder().credential(creds).vaultUrl(KEY_VAULT_URL).buildClient();
                    
                    KeyVaultKey key = keyClient.getKey(RSA2048_KEY_NAME);
                    CryptographyClient cryptoClient = new CryptographyClientBuilder()
        	                .keyIdentifier(key.getId())
        	                .credential(creds)
        	                .buildClient();

                    EncryptResult encryptResponse = cryptoClient.encrypt(EncryptionAlgorithm.RSA_OAEP_256, aesKey);
                    
                    String ivBase64 = Base64.getEncoder().encodeToString(iv);
                    String cipherText = Base64.getEncoder().encodeToString(ciphertext);

                    String encryptedAesKeyBase64 = Base64.getEncoder().encodeToString(encryptResponse.getCipherText());
                    // Process the request and create response object
                    rsa2048_encryptResponseMessage responseObj = new rsa2048_encryptResponseMessage(ivBase64, cipherText, encryptedAesKeyBase64);

                    // Convert response object to JSON string
                    String jsonResponse = objectMapper.writeValueAsString(responseObj);

                    return request.createResponseBuilder(HttpStatus.OK).body(jsonResponse).build();
                } catch (Exception e) {
                    return request.createResponseBuilder(HttpStatus.BAD_REQUEST).body("Error: " + e.getMessage()).build();
                }
    }

}
