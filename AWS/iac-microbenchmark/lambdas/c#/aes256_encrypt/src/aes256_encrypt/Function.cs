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
    // Struct representing the incoming request from body
    public struct aes256_encryptRequest
    {
        public string Message { get; set; }
    }

    // Struct representing the outgoing response into body
    public struct aes256_encryptResponse
    {
        public string EncryptedMessage { get; set; }
        public string EncryptedDataKey { get; set; }
        public string Iv { get; set; }
        public string Tag { get; set; }

    }

    public class Function
    {
        // Create the KMS client
        private static readonly IAmazonKeyManagementService kmsClient = new AmazonKeyManagementServiceClient(RegionEndpoint.USEast1);
        // The Lambda handler function
        public async Task<APIGatewayHttpApiV2ProxyResponse> FunctionHandler(APIGatewayHttpApiV2ProxyRequest request, ILambdaContext context)
        {
            // Build APIGW response
            var APIGWResponse = new APIGatewayHttpApiV2ProxyResponse
            {
                Headers = new Dictionary<string, string>
            {
                { "Content-Type", "application/json" },
                {"Access-Control-Allow-Origin", "*"}
            }
            };

            string KMSKEYARNNAME = "AES_KMS_KEY_ARN";

            // Get the value of the environment variable
            string? KMSKEYARNVALUE = Environment.GetEnvironmentVariable(KMSKEYARNNAME);

            // Check if the variable is found
            if (string.IsNullOrEmpty(KMSKEYARNVALUE))
            {
                Console.WriteLine($"Environment variable '{KMSKEYARNNAME}' is not set.");

                // Log the exception and return a 500 error response
                var errorRsp = new Dictionary<string, string>
            {
                { "Error", $"Environment variable '{KMSKEYARNNAME}' is not set." }
            };

                APIGWResponse.StatusCode = 500;
                APIGWResponse.Body = JsonSerializer.Serialize(errorRsp);

                return APIGWResponse;
            }

            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };
                // Deserialize the incoming request body into the RequestModel struct
                var requestModel = JsonSerializer.Deserialize<aes256_encryptRequest>(request.Body, options);

                // Generate a new data key from KMS
                var generateDataKeyRequest = new GenerateDataKeyRequest
                {
                    KeyId = KMSKEYARNVALUE,
                    KeySpec = DataKeySpec.AES_256
                };

                var dataKeyResponse = await kmsClient.GenerateDataKeyAsync(generateDataKeyRequest);
                var plaintextDataKey = dataKeyResponse.Plaintext.ToArray();
                var encryptedDataKey = dataKeyResponse.CiphertextBlob.ToArray();
                var message = Encoding.UTF8.GetBytes(requestModel.Message);

                // Do physical Encryption here, create response
                var responseModel = AESGCMEncrypt(plaintextDataKey, message, encryptedDataKey);

                // Serialize the response model into a JSON string
                var responseBody = JsonSerializer.Serialize(responseModel);

                // Return a successful response with the serialized response body
                APIGWResponse.Body = responseBody;
                APIGWResponse.StatusCode = 200;

                return APIGWResponse;
            }
            catch (Exception ex)
            {
                // Log the exception and return a 500 error response
                context.Logger.LogError($"Error processing request for aes256_encrypt c#: {ex.Message}");
                var errorRsp = new Dictionary<string, string>
            {
                { "Error", $"Error processing request for aes256_encrypt c#: {ex.Message}" }
            };

                APIGWResponse.StatusCode = 500;
                APIGWResponse.Body = JsonSerializer.Serialize(errorRsp);

                return APIGWResponse;
            }
        }

        public static LambdaApiProxy.aes256_encryptResponse AESGCMEncrypt(byte[] plaintextDataKey, byte[] message, byte[] encryptedDataKey)
        {
            // Generate a secure random 12-byte IV for AES-GCM
            int iv_size = 12;

            byte[] iv = new byte[iv_size];

            using (var rng = RandomNumberGenerator.Create())
            {
                rng.GetBytes(iv);
            }

            byte[] encryptedMessage;

            byte[] tag;

            int tag_size = 16;

            using (var aesGcm = new AesGcm(plaintextDataKey, tag_size))
            {

                encryptedMessage = new byte[message.Length];

                tag = new byte[tag_size];

                // Encrypt the message
                aesGcm.Encrypt(iv, message, encryptedMessage, tag);
            }

            // Create a response model with a message
            var responseModel = new aes256_encryptResponse
            {
                EncryptedDataKey = Convert.ToBase64String(encryptedDataKey),
                Iv = Convert.ToBase64String(iv),
                Tag = Convert.ToBase64String(tag),
                EncryptedMessage = Convert.ToBase64String(encryptedMessage),
            };

            return responseModel;

        }
    }
}
