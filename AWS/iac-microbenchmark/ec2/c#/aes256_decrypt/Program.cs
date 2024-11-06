using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using Amazon;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;

namespace Program
{
    // Struct representing the incoming request for decryption
    public struct aes256_decryptRequest
    {
        public string EncryptedMessage { get; set; }
        public string EncryptedDataKey { get; set; }
        public string Iv { get; set; }
        public string Tag { get; set; }
    }

    // Struct representing the outgoing response after decryption
    public struct aes256_decryptResponse
    {
        public string Message { get; set; }
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
            aes256_decryptRequest request;
            try
            {
                request = JsonSerializer.Deserialize<aes256_decryptRequest>(args[0]);
            }
            catch (JsonException)
            {
                Console.WriteLine("Error: Invalid JSON input.");
                return;
            }

            try
            {
                // Decrypt the data key using KMS
                var decryptRequest = new DecryptRequest
                {
                    CiphertextBlob = new MemoryStream(Convert.FromBase64String(request.EncryptedDataKey)),
                    KeyId = kmsKeyArn
                };

                var decryptedKeyResponse = await kmsClient.DecryptAsync(decryptRequest);
                byte[] plaintextDataKey = decryptedKeyResponse.Plaintext.ToArray();

                // Prepare for decryption of the message
                var iv = Convert.FromBase64String(request.Iv);
                var tag = Convert.FromBase64String(request.Tag);
                var encryptedMessage = Convert.FromBase64String(request.EncryptedMessage);
                var decryptedMessageBytes = new byte[encryptedMessage.Length];

                int tag_size = 16;
                // Decrypt the message using AES-GCM
                using (var aesGcm = new AesGcm(plaintextDataKey, tag_size))
                {
                    aesGcm.Decrypt(iv, encryptedMessage, tag, decryptedMessageBytes);
                }

                // Create response object with decrypted data
                var response = new aes256_decryptResponse
                {
                    Message = Encoding.UTF8.GetString(decryptedMessageBytes)
                };

                // Output the JSON result to console
                Console.WriteLine(JsonSerializer.Serialize(response));
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error during decryption: {ex.Message}");
            }
        }
    }
}
