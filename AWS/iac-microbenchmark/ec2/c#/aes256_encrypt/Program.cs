using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using Amazon;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;

namespace Program
{
    // Struct representing the incoming request
    public struct aes256_encryptRequest
    {
        public string Message { get; set; }
    }

    // Struct representing the outgoing response
    public struct aes256_encryptResponse
    {
        public string EncryptedMessage { get; set; }
        public string EncryptedDataKey { get; set; }
        public string Iv { get; set; }
        public string Tag { get; set; }
    }

    public class Program
    {
        private static readonly string KMSKEYARNNAME = "AES_KMS_KEY_ARN";
        private static readonly IAmazonKeyManagementService kmsClient = new AmazonKeyManagementServiceClient(RegionEndpoint.USEast1);

        public static async Task Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("Please provide a JSON string as an argument.");
                return;
            }

            // Retrieve KMS Key ARN from environment variable
            string? kmsKeyArn = Environment.GetEnvironmentVariable(KMSKEYARNNAME);
            if (string.IsNullOrEmpty(kmsKeyArn))
            {
                Console.WriteLine($"Error: KMS Key ARN environment variable '{KMSKEYARNNAME}' is not set.");
                return;
            }

            // Parse JSON input from command line argument
            aes256_encryptRequest request;
            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };
                request = JsonSerializer.Deserialize<aes256_encryptRequest>(args[0], options);
            }
            catch (JsonException)
            {
                Console.WriteLine("Error: Invalid JSON input.");
                return;
            }

            try
            {
                // Generate a new data key from KMS
                var generateDataKeyRequest = new GenerateDataKeyRequest
                {
                    KeyId = kmsKeyArn,
                    KeySpec = DataKeySpec.AES_256
                };

                var dataKeyResponse = await kmsClient.GenerateDataKeyAsync(generateDataKeyRequest);
                var plaintextDataKey = dataKeyResponse.Plaintext.ToArray();
                var encryptedDataKey = dataKeyResponse.CiphertextBlob.ToArray();

                // Generate a secure random IV for AES-GCM
                int iv_size = 12;
                int tag_size = 16;
                byte[] iv = new byte[iv_size];
                using (var rng = RandomNumberGenerator.Create())
                {
                    rng.GetBytes(iv);
                }

                // Encrypt the message
                var encryptedMessageBytes = new byte[request.Message.Length];
                byte[] tag = new byte[tag_size];
                using (var aesGcm = new AesGcm(plaintextDataKey, 16))
                {
                    aesGcm.Encrypt(iv, Encoding.UTF8.GetBytes(request.Message), encryptedMessageBytes, tag);
                }

                // Create response object with encrypted data and encode as Base64
                var response = new aes256_encryptResponse
                {
                    EncryptedMessage = Convert.ToBase64String(encryptedMessageBytes),
                    EncryptedDataKey = Convert.ToBase64String(encryptedDataKey),
                    Iv = Convert.ToBase64String(iv),
                    Tag = Convert.ToBase64String(tag)
                };

                // Output the JSON result to console
                Console.WriteLine(JsonSerializer.Serialize(response));
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error during encryption: {ex.Message}");
            }
        }
    }
}
