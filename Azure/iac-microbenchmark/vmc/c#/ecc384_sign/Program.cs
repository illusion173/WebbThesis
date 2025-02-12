using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using Azure;
using Azure.Core;
using Azure.Identity;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;

namespace Program
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
                Console.WriteLine($"{{ \"Error\": \"Environment variable  AZURE_KEY_VAULT_URL is not set.\" }}");
                return;
            }


            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };
                var requestModel = JsonSerializer.Deserialize<ecc384_signRequest>(args[0], options);

                // Convert hex string to byte array
                byte[] messageDigestBytes;
                try
                {
                    messageDigestBytes = Convert.FromHexString(requestModel.message_digest);
                }
                catch (FormatException)
                {
                    Console.WriteLine("{\"Error\": \"Invalid hex format in 'message_digest'.\"}");
                    return;
                }

                // Put main code here
                try
                {
                    var keyClient = new KeyClient(new Uri(AZURE_KEY_VAULT_URL), credential);

                    // Get the key from Azure Key Vault
                    KeyVaultKey key = keyClient.GetKey(ECC384_KEY_NAME);

                    // Initialize the cryptography client for signing
                    var cryptoClient = new CryptographyClient(key.Id, credential);

                    // Perform ECC signature
                    SignResult signResult = cryptoClient.Sign(SignatureAlgorithm.ES384, messageDigestBytes);

                    // Convert signature to Base64
                    string signatureB64 = Convert.ToBase64String(signResult.Signature);

                    Console.WriteLine(JsonSerializer.Serialize(new ecc384_signResponse { signature = signatureB64 }));
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"{{ \"Error\": \"Error doing Operation ecc384_sign: {ex.Message}\" }}");
                }

            }
            catch (JsonException)
            {
                Console.WriteLine("{\"Error\": \"Invalid JSON format. Please provide a valid JSON input.\"}");
            }
        }

    }

}
