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
    public struct rsa3072_encryptRequest
    {
        public string Message { get; set; }
    }

    // Struct representing the outgoing response into body
    public struct rsa3072_encryptResponse
    {
        public string CipherText { get; set; }
        public string Iv { get; set; }
        public string EncryptedAesKey { get; set; }
    }

    public class Function
    {

        // Create the KMS client
        private static readonly IAmazonKeyManagementService kmsClient = new AmazonKeyManagementServiceClient(RegionEndpoint.USEast1);


        // The Lambda handler function
        public async Task<APIGatewayProxyResponse> FunctionHandler(APIGatewayProxyRequest request, ILambdaContext context)
        {
            // Build APIGW response
            var APIGWResponse = new APIGatewayProxyResponse
            {
                Headers = new Dictionary<string, string>
            {
                { "Content-Type", "application/json" },
                {"Access-Control-Allow-Origin", "*"}
            }
            };


            string KMSKEYARNNAME = "RSA3072_KMS_KEY_ARN";

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
                // Deserialize the incoming request body into the RequestModel struct
                var requestModel = JsonSerializer.Deserialize<rsa3072_encryptRequest>(request.Body);

                String plaintext = requestModel.Message;

                // Generate AES key and IV
                byte[] aesKey = new byte[32];
                byte[] iv = new byte[16];

                RandomNumberGenerator.Fill(aesKey);  // Fill the array with random bytes
                RandomNumberGenerator.Fill(iv);

                byte[] CipherText = AESCTREncrypt(plaintext, aesKey, iv);

                // Encrypt the AES key using KMS
                var encryptRequest = new EncryptRequest
                {
                    KeyId = KMSKEYARNVALUE,
                    Plaintext = new MemoryStream(aesKey),
                    EncryptionAlgorithm = "RSAES_OAEP_SHA_256"
                };

                var encryptResponse = await kmsClient.EncryptAsync(encryptRequest);

                byte[] encryptedAESKey = encryptResponse.CiphertextBlob.ToArray();

                // Create a response model with a message
                var responseModel = new rsa3072_encryptResponse
                {
                    CipherText = Convert.ToBase64String(CipherText),
                    EncryptedAesKey = Convert.ToBase64String(encryptedAESKey),
                    Iv = Convert.ToBase64String(iv)
                };

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
                context.Logger.LogError($"Error processing request for rsa3072_encrypt c#: {ex.Message}");
                var errorRsp = new Dictionary<string, string>
            {
                { "Error", $"Error processing request for rsa3072_encrypt c#: {ex.Message}" }
            };

                APIGWResponse.StatusCode = 500;
                APIGWResponse.Body = JsonSerializer.Serialize(errorRsp);

                return APIGWResponse;
            }
        }

        public static byte[] AESCTREncrypt(string plaintext, byte[] key, byte[] iv)
        {
            // Create AES instance
            using (Aes aes = Aes.Create())
            {
                aes.Key = key;
                aes.Mode = CipherMode.ECB; // ECB to avoid built-in chaining
                aes.Padding = PaddingMode.None; // No padding, as CTR does not need it

                // Convert plaintext to byte array
                byte[] inputBytes = Encoding.UTF8.GetBytes(plaintext);
                byte[] outputBytes = new byte[inputBytes.Length];

                // AES block size is 128 bits (16 bytes)
                int blockSize = aes.BlockSize / 8;
                byte[] counter = new byte[blockSize];
                Buffer.BlockCopy(iv, 0, counter, 0, iv.Length);

                // Process each block
                using (ICryptoTransform encryptor = aes.CreateEncryptor())
                {
                    for (int i = 0; i < inputBytes.Length; i += blockSize)
                    {
                        // Encrypt the counter
                        byte[] encryptedCounter = new byte[blockSize];
                        encryptor.TransformBlock(counter, 0, blockSize, encryptedCounter, 0);

                        // XOR plaintext block with the encrypted counter block
                        for (int j = 0; j < blockSize && i + j < inputBytes.Length; j++)
                        {
                            outputBytes[i + j] = (byte)(inputBytes[i + j] ^ encryptedCounter[j]);
                        }

                        // Increment the counter after processing each block
                        IncrementCounter(counter);
                    }
                }

                return outputBytes;
            }
        }

        private static void IncrementCounter(byte[] counter)
        {
            for (int i = counter.Length - 1; i >= 0; i--)
            {
                if (++counter[i] != 0)
                    break; // If no overflow, we are done
            }
        }
    }
}
