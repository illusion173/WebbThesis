using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;
using Azure.Identity;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;

namespace dotnet_ecc384_verify
{
    // Struct representing the incoming request
    public struct ecc384_verifyRequest
    {
        public string message_digest { get; set; }
        public string signature { get; set; }
    }

    // Struct representing the outgoing response
    public struct ecc384_verifyResponse
    {
        public bool is_valid { get; set; }
    }

    public class ecc384_verify_program
    {
        private readonly ILogger<ecc384_verify_program> _logger;

        public ecc384_verify_program(ILogger<ecc384_verify_program> logger)
        {
            _logger = logger;
        }

        [Function("dotnet_ecc384_verify_program")]
        public static async Task<IActionResult> Run([HttpTrigger(AuthorizationLevel.Anonymous, "post")] HttpRequest req)
        {
            string? ECC384_KEY_NAME = Environment.GetEnvironmentVariable("ECC384_KEY_NAME");
            string? AZURE_KEY_VAULT_URL = Environment.GetEnvironmentVariable("AZURE_KEY_VAULT_URL");

            if (string.IsNullOrEmpty(ECC384_KEY_NAME) || string.IsNullOrEmpty(AZURE_KEY_VAULT_URL))
            {
                return new BadRequestObjectResult(new { error = "Environment variables may be missing." });
            }

            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };

                string requestBodyStr = await new StreamReader(req.Body).ReadToEndAsync();
                var requestModel = JsonSerializer.Deserialize<ecc384_verifyRequest>(requestBodyStr, options);

                if (requestModel.message_digest == null || requestModel.signature == null)
                {
                    return new BadRequestObjectResult(new { error = "Invalid request payload." });
                }

                byte[] signatureBytes = Convert.FromBase64String(requestModel.signature);

                // Convert hex string to byte array
                byte[] messageDigestBytes;
                try
                {
                    messageDigestBytes = Convert.FromHexString(requestModel.message_digest);
                }
                catch (FormatException)
                {
                    return new BadRequestObjectResult(new { error = "Invalid hex format for message_digest." });
                }

                try
                {
                    var credential = new DefaultAzureCredential();
                    var keyClient = new KeyClient(new Uri(AZURE_KEY_VAULT_URL), credential);

                    // Get the key from Azure Key Vault
                    KeyVaultKey key = await keyClient.GetKeyAsync(ECC384_KEY_NAME);

                    // Initialize the cryptography client for verification
                    var cryptoClient = new CryptographyClient(key.Id, credential);
                    VerifyResult verifyResult = await cryptoClient.VerifyAsync(SignatureAlgorithm.ES384, messageDigestBytes, signatureBytes);

                    return new OkObjectResult(new ecc384_verifyResponse { is_valid = verifyResult.IsValid });
                }
                catch (Exception ex)
                {
                    return new BadRequestObjectResult(new { error = ex.Message });
                }
            }
            catch (JsonException)
            {
                return new BadRequestObjectResult(new { error = "Invalid JSON payload." });
            }
        }
    }
}
