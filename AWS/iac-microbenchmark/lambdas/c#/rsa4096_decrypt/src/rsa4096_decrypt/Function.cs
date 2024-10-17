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
    public struct rsa4096_decryptRequest
    {
        public string CipherText { get; set; }
        public string Iv { get; set; }
        public string EncryptedAesKey { get; set; }

    }

    // Struct representing the outgoing response into body
    public struct rsa4096_decryptResponse
    {
        public string Message { get; set; }
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

            string KMSKEYARNNAME = "RSA4096_KMS_KEY_ARN";

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
                var requestModel = JsonSerializer.Deserialize<rsa4096_decryptRequest>(request.Body);

                byte[] Iv = Convert.FromBase64String(requestModel.Iv);

                byte[] EncryptedAesKey = Convert.FromBase64String(requestModel.EncryptedAesKey);

                byte[] CipherText = Convert.FromBase64String(requestModel.CipherText);


                // Create the request object
                var decryptRequest = new DecryptRequest
                {
                    CiphertextBlob = new MemoryStream(EncryptedAesKey),  // The encrypted AES key (CiphertextBlob)
                    KeyId = KMSKEYARNVALUE,
                    EncryptionAlgorithm = EncryptionAlgorithmSpec.RSAES_OAEP_SHA_256  // Specify the encryption algorithm
                };

                // Call the DecryptAsync method
                DecryptResponse decryptResponse = await kmsClient.DecryptAsync(decryptRequest);

                // Get the decrypted AES key (in plaintext)
                byte[] decryptedAesKey = decryptResponse.Plaintext.ToArray();

                String plaintext = Encoding.UTF8.GetString(AESCTRDecrypt(CipherText, decryptedAesKey, Iv));

                // Create a response model with a message
                var responseModel = new rsa4096_decryptResponse
                {
                    Message = plaintext,
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
                context.Logger.LogError($"Error processing request for rsa4096_decrypt c#: {ex.Message}");
                var errorRsp = new Dictionary<string, string>
            {
                { "Error", $"Error processing request for rsa4096_decrypt c#: {ex.Message}" }
            };

                APIGWResponse.StatusCode = 500;
                APIGWResponse.Body = JsonSerializer.Serialize(errorRsp);

                return APIGWResponse;
            }
        }

        public static byte[] AESCTRDecrypt(byte[] ciphertext, byte[] key, byte[] iv)
        {
            // Create AES instance
            using (Aes aes = Aes.Create())
            {
                aes.Key = key;
                aes.Mode = CipherMode.ECB; // ECB mode to avoid built-in chaining
                aes.Padding = PaddingMode.None; // No padding, as CTR does not need it

                // AES block size is 128 bits (16 bytes)
                int blockSize = aes.BlockSize / 8;
                byte[] counter = new byte[blockSize];
                Buffer.BlockCopy(iv, 0, counter, 0, iv.Length);

                byte[] outputBytes = new byte[ciphertext.Length];

                // Decrypt block-by-block
                using (ICryptoTransform encryptor = aes.CreateEncryptor())
                {
                    for (int i = 0; i < ciphertext.Length; i += blockSize)
                    {
                        // Encrypt the counter
                        byte[] encryptedCounter = new byte[blockSize];
                        encryptor.TransformBlock(counter, 0, blockSize, encryptedCounter, 0);

                        // XOR ciphertext block with the encrypted counter block
                        for (int j = 0; j < blockSize && i + j < ciphertext.Length; j++)
                        {
                            outputBytes[i + j] = (byte)(ciphertext[i + j] ^ encryptedCounter[j]);
                        }

                        // Increment the counter after each block
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
