using Amazon.Lambda.Core;
using Amazon.Lambda.APIGatewayEvents;
using System.Text.Json;
using System.Security.Cryptography;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;
using Amazon;
using System.Text;

// Assembly attribute to enable the Lambda function's JSON input to be converted into .NET types
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace LambdaApiProxy
{
    // Struct representing the incoming request body
    public struct aes256_decryptRequest
    {
        public string EncryptedMessage { get; set; }
        public string EncryptedDataKey { get; set; }
        public string Iv { get; set; }
        public string Tag { get; set; }
    }

    // Struct representing the outgoing response body
    public struct aes256_decryptResponse
    {
        public string Message { get; set; }
    }

    public class Function
    {
        // Create the KMS client
        private static readonly IAmazonKeyManagementService kmsClient = new AmazonKeyManagementServiceClient(RegionEndpoint.USEast1);

        // The Lambda handler function
        public async Task<APIGatewayHttpApiV2ProxyResponse> FunctionHandler(APIGatewayHttpApiV2ProxyRequest request, ILambdaContext context)
        {
            var APIGWResponse = new APIGatewayHttpApiV2ProxyResponse
            {
                Headers = new Dictionary<string, string>
                {
                    { "Content-Type", "application/json" },
                    { "Access-Control-Allow-Origin", "*" }
                }
            };

            string KMSKEYARNNAME = "AES_KMS_KEY_ARN";
            string? KMSKEYARNVALUE = Environment.GetEnvironmentVariable(KMSKEYARNNAME);

            if (string.IsNullOrEmpty(KMSKEYARNVALUE))
            {
                context.Logger.LogError($"Environment variable '{KMSKEYARNNAME}' is not set.");
                APIGWResponse.StatusCode = 500;
                APIGWResponse.Body = JsonSerializer.Serialize(new { Error = $"Environment variable '{KMSKEYARNNAME}' is not set." });
                return APIGWResponse;
            }

            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };
                var requestModel = JsonSerializer.Deserialize<aes256_decryptRequest>(request.Body, options);

                // Decrypt the data key using KMS
                var decryptRequest = new DecryptRequest
                {
                    CiphertextBlob = new MemoryStream(Convert.FromBase64String(requestModel.EncryptedDataKey)),
                    KeyId = KMSKEYARNVALUE
                };
                var decryptedKeyResponse = await kmsClient.DecryptAsync(decryptRequest);
                byte[] plaintextDataKey = decryptedKeyResponse.Plaintext.ToArray();

                // Decode IV, Tag, and EncryptedMessage from base64
                byte[] iv = Convert.FromBase64String(requestModel.Iv);
                byte[] encryptedMessage = Convert.FromBase64String(requestModel.EncryptedMessage);
                byte[] tag = Convert.FromBase64String(requestModel.Tag);

                // Decrypt message
                string decryptedMessage = AESGCMDecrypt(encryptedMessage, plaintextDataKey, iv, tag);

                // Prepare the response
                var responseModel = new aes256_decryptResponse { Message = decryptedMessage };
                APIGWResponse.Body = JsonSerializer.Serialize(responseModel);
                APIGWResponse.StatusCode = 200;

                return APIGWResponse;
            }
            catch (Exception ex)
            {
                context.Logger.LogError($"Error processing request for aes256_decrypt: {ex.Message}");
                APIGWResponse.StatusCode = 500;
                APIGWResponse.Body = JsonSerializer.Serialize(new { Error = $"Error processing request: {ex.Message}" });
                return APIGWResponse;
            }
        }

        public static string AESGCMDecrypt(byte[] ciphertext, byte[] key, byte[] iv, byte[] tag)
        {

            var decryptedMessageBytes = new byte[ciphertext.Length];
            int tag_size = 16;
            // Decrypt the message using AES-GCM
            using (var aesGcm = new AesGcm(key, tag_size))
            {
                aesGcm.Decrypt(iv, ciphertext, tag, decryptedMessageBytes);
            }
            return Encoding.UTF8.GetString(decryptedMessageBytes);

        }

    }
}
