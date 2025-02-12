using System.Text.Json;
using Azure.Identity;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;

namespace Program
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

    public class Program
    {
        public static void Main(string[] args)
        {

            var credential = new AzureCliCredential();

            if (args.Length == 0)
            {
                Console.WriteLine("{\"Error\": \"Please provide JSON input as an argument.\"}");
                return;
            }

            string? ECC384_KEY_NAME = Environment.GetEnvironmentVariable("ECC384_KEY_NAME");
            string? AZURE_KEY_VAULT_URL = Environment.GetEnvironmentVariable("AZURE_KEY_VAULT_URL");

            if (string.IsNullOrEmpty(ECC384_KEY_NAME))
            {
                Console.WriteLine($"{{ \"Error\": \"Environment variable ECC384_KEY_NAME is not set.\" }}");
                return;
            }

            if (string.IsNullOrEmpty(AZURE_KEY_VAULT_URL))
            {
                Console.WriteLine($"{{ \"Error\": \"Environment variable AZURE_KEY_VAULT_URL is not set.\" }}");
                return;
            }


            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };
                var requestModel = JsonSerializer.Deserialize<ecc384_verifyRequest>(args[0], options);
                if (string.IsNullOrEmpty(requestModel.message_digest) || string.IsNullOrEmpty(requestModel.signature))
                {

                    Console.WriteLine("{\"Error\": \"Invalid JSON format, something is null. Please provide a valid JSON input.\"}");
                    return;
                }

                try
                {
                    var keyClient = new KeyClient(new Uri(AZURE_KEY_VAULT_URL), credential);

                    // Get the key from Azure Key Vault
                    KeyVaultKey key = keyClient.GetKey(ECC384_KEY_NAME);

                    // Initialize the cryptography client for signing
                    var cryptoClient = new CryptographyClient(key.Id, credential);

                    byte[] messageDigestBytes = Convert.FromHexString(requestModel.message_digest);
                    byte[] signatureBytes = Convert.FromBase64String(requestModel.signature);

                    VerifyResult verifyResult = cryptoClient.Verify(SignatureAlgorithm.ES384, messageDigestBytes, signatureBytes);

                    Console.WriteLine(JsonSerializer.Serialize(new ecc384_verifyResponse { is_valid = verifyResult.IsValid }));


                }
                catch (Exception ex)
                {
                    Console.WriteLine($"{{ \"Error\": \"Error doing Operation ecc384_verify: {ex.Message}\" }}");
                }

            }
            catch (JsonException)
            {
                Console.WriteLine("{\"Error\": \"Invalid JSON format. Please provide a valid JSON input.\"}");
            }
        }

    }

}
