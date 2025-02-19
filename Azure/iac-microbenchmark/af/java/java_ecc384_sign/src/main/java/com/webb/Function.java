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
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import java.util.Optional;
import com.azure.security.keyvault.keys.cryptography.models.SignResult;
import com.azure.security.keyvault.keys.cryptography.models.SignatureAlgorithm;

/**
 * Azure Functions with HTTP Trigger.
 */
public class Function {

    private static final String KEY_VAULT_URL = System.getenv("AZURE_KEY_VAULT_URL");
    private static final String ECC384_KEY_NAME = System.getenv("ECC384_KEY_NAME");
    private static final ObjectMapper objectMapper = new ObjectMapper();

    
    @FunctionName("java_ecc384_sign")
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


                    ecc384_signRequestMessage ecc384_signrequest = objectMapper.readValue(requestBody, ecc384_signRequestMessage.class);


                    byte[] messageDigestBytes = hexStringToByteArray(ecc384_signrequest.getmessage_digest());                    
                    DefaultAzureCredential creds = new DefaultAzureCredentialBuilder().build();

                    
                    KeyClient keyClient = new KeyClientBuilder().credential(creds).vaultUrl(KEY_VAULT_URL).buildClient();
                    
                    KeyVaultKey key = keyClient.getKey(ECC384_KEY_NAME);
                    CryptographyClient cryptoClient = new CryptographyClientBuilder()
        	                .keyIdentifier(key.getId())
        	                .credential(creds)
        	                .buildClient();
                    
                    
                    SignResult signResult = cryptoClient.sign(SignatureAlgorithm.ES384, messageDigestBytes);
             
                    String signatureBase64 = Base64.getEncoder().encodeToString(signResult.getSignature());
             

                    // Process the request and create response object
                    ecc384_signResponseMessage responseObj = new ecc384_signResponseMessage(signatureBase64);

                    // Convert response object to JSON string
                    String jsonResponse = objectMapper.writeValueAsString(responseObj);

                    return request.createResponseBuilder(HttpStatus.OK).body(jsonResponse).build();
                } catch (Exception e) {
                    return request.createResponseBuilder(HttpStatus.BAD_REQUEST).body("Error: " + e.getMessage()).build();
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
