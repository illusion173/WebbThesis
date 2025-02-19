using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;
using Azure.Identity;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;

namespace dotnet_ecc384_sign
{
    // Struct representing the incoming request
    public struct ecc384_signRequest
    {
        public string message_digest { get; set; }
    }

    // Struct representing the outgoing response
    public struct ecc384_signResponse
    {
        public string signature { get; set; }
    }

    public class ecc384_sign_program
    {
        private readonly ILogger<ecc384_sign_program> _logger;

        public ecc384_sign_program(ILogger<ecc384_sign_program> logger)
        {
            _logger = logger;
        }

        [Function("dotnet_ecc384_sign_program")]
        public static async Task<IActionResult> Run([HttpTrigger(AuthorizationLevel.Anonymous, "post")] HttpRequest req)
        {
            string? ECC384_KEY_NAME = Environment.GetEnvironmentVariable("ECC384_KEY_NAME");
            string? AZURE_KEY_VAULT_URL = Environment.GetEnvironmentVariable("AZURE_KEY_VAULT_URL");

            if (string.IsNullOrEmpty(ECC384_KEY_NAME) || string.IsNullOrEmpty(AZURE_KEY_VAULT_URL))
            {
                return new BadRequestObjectResult(new { error = "EnvVar may be missing." });
            }

            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };

                string requestBodyStr = await new StreamReader(req.Body).ReadToEndAsync();
                var requestModel = JsonSerializer.Deserialize<ecc384_signRequest>(requestBodyStr, options);

                if (string.IsNullOrEmpty(requestModel.message_digest))
                {
                    return new BadRequestObjectResult(new { error = "Invalid request payload." });
                }

                // Convert hex string to byte array
                byte[] messageDigestBytes;
                try
                {
                    messageDigestBytes = Convert.FromHexString(requestModel.message_digest);
                }
                catch (FormatException ex)
                {
                    return new BadRequestObjectResult(new { error = "Invalid hex string: " + ex.Message });
                }

                try
                {
                    var credential = new DefaultAzureCredential();
                    var keyClient = new KeyClient(new Uri(AZURE_KEY_VAULT_URL), credential);

                    // Get the key from Azure Key Vault asynchronously
                    KeyVaultKey key = await keyClient.GetKeyAsync(ECC384_KEY_NAME);

                    // Initialize the cryptography client for signing
                    var cryptoClient = new CryptographyClient(key.Id, credential);

                    // Perform ECC signature asynchronously
                    SignResult signResult = await cryptoClient.SignAsync(SignatureAlgorithm.ES384, messageDigestBytes);

                    // Convert signature to Base64
                    string signatureB64 = Convert.ToBase64String(signResult.Signature);

                    return new OkObjectResult(new ecc384_signResponse { signature = signatureB64 });
                }
                catch (Exception ex)
                {
                    return new ObjectResult(new { error = "Key Vault Error: " + ex.Message }) { StatusCode = 500 };
                }
            }
            catch (JsonException)
            {
                return new BadRequestObjectResult(new { error = "Invalid JSON format." });
            }
        }
    }
}
