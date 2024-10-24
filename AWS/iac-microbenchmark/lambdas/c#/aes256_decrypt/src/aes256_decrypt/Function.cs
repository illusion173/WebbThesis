using Amazon.Lambda.Core;
using Amazon.Lambda.APIGatewayEvents;
using System.Text.Json;
using System.Collections.Generic;
using System;
using System.Security.Cryptography;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;
using Amazon;

// Assembly attribute to enable the Lambda function's JSON input to be converted into .NET types
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace LambdaApiProxy
{

    // Struct representing the outgoing response into body
    public struct aes256_decryptRequest
    {
        public string EncryptedMessage { get; set; }
        public string EncryptedDataKey { get; set; }
        public string Iv { get; set; }
        public string Tag { get; set; }

    }

    // Struct representing the incoming request from body
    public struct aes256_decryptResponse
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
                // Deserialize the incoming request body into the RequestModel struct
                var requestModel = JsonSerializer.Deserialize<aes256_decryptRequest>(request.Body);



                // Create a response model with a message
                var responseModel = new aes256_decryptResponse
                {
                    Message = "",
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
                context.Logger.LogError($"Error processing request for aes256_decrypt c#: {ex.Message}");
                var errorRsp = new Dictionary<string, string>
            {
                { "Error", $"Error processing request for aes256_decrypt c#: {ex.Message}" }
            };

                APIGWResponse.StatusCode = 500;
                APIGWResponse.Body = JsonSerializer.Serialize(errorRsp);

                return APIGWResponse;
            }
        }
        public static byte[] AESCTREncrypt(string plaintext, byte[] key, byte[] iv)
        {
            using (Aes aes = Aes.Create())
            {
                aes.Key = key;
                aes.IV = iv;

                // Set the mode to CTR (Counter Mode)
                aes.Mode = CipherMode.ECB; // ECB mode as a workaround, we will handle counter ourselves
                aes.Padding = PaddingMode.None; // No padding, we will handle the block size

                using (MemoryStream ms = new MemoryStream())
                {
                    using (CryptoStream cs = new CryptoStream(ms, aes.CreateEncryptor(), CryptoStreamMode.Write))
                    {
                        // Convert plaintext to byte array
                        byte[] inputBytes = System.Text.Encoding.UTF8.GetBytes(plaintext);

                        // AES block size
                        int blockSize = aes.BlockSize / 8; // BlockSize is in bits, convert to bytes

                        // Counter initialization
                        byte[] counter = new byte[blockSize];
                        Buffer.BlockCopy(iv, 0, counter, 0, blockSize);

                        // Encrypt using CTR mode
                        for (int i = 0; i < inputBytes.Length; i++)
                        {
                            if (i % blockSize == 0 && i != 0) // Increment counter after each block
                            {
                                IncrementCounter(counter);
                            }

                            byte[] block = new byte[1] { inputBytes[i] };
                            cs.Write(block, 0, block.Length);
                            cs.WriteByte((byte)(block[0] ^ counter[i % blockSize])); // XOR with the counter
                        }
                    }

                    return ms.ToArray();
                }
            }
        }

        public static string AESCTRDecrypt(byte[] ciphertext, byte[] key, byte[] iv)
        {
            using (Aes aes = Aes.Create())
            {
                aes.Key = key;

                // Set the mode to ECB
                aes.Mode = CipherMode.ECB; // ECB mode as a workaround, we will handle counter ourselves
                aes.Padding = PaddingMode.None; // No padding, we will handle the block size

                using (MemoryStream ms = new MemoryStream())
                {
                    // AES block size
                    int blockSize = aes.BlockSize / 8; // BlockSize is in bits, convert to bytes

                    // Counter initialization
                    byte[] counter = new byte[blockSize];
                    Buffer.BlockCopy(iv, 0, counter, 0, blockSize);

                    // Decrypt using CTR mode
                    for (int i = 0; i < ciphertext.Length; i++)
                    {
                        if (i % blockSize == 0 && i != 0) // Increment counter after each block
                        {
                            IncrementCounter(counter);
                        }

                        byte[] block = new byte[1] { ciphertext[i] };
                        byte decryptedByte = (byte)(block[0] ^ counter[i % blockSize]); // XOR with the counter
                        ms.WriteByte(decryptedByte);
                    }

                    return System.Text.Encoding.UTF8.GetString(ms.ToArray());
                }
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
