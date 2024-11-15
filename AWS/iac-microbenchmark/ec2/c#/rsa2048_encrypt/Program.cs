using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using Amazon;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;

namespace Program
{
    // Struct representing the incoming request
    public struct rsa2048_encryptRequest
    {
        public string Message { get; set; }
    }

    // Struct representing the outgoing response
    public struct rsa2048_encryptResponse
    {
        public string CipherText { get; set; }
        public string Iv { get; set; }
        public string EncryptedAesKey { get; set; }
    }

    public class Program
    {
        private static readonly IAmazonKeyManagementService kmsClient = new AmazonKeyManagementServiceClient(RegionEndpoint.USEast1);

        public static async Task Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("{\"Error\": \"Please provide JSON input as an argument.\"}");
                return;
            }

            string KMSKEYARNNAME = "RSA2048_KMS_KEY_ARN";
            string? kmsKeyArn = Environment.GetEnvironmentVariable(KMSKEYARNNAME);

            if (string.IsNullOrEmpty(kmsKeyArn))
            {
                Console.WriteLine($"{{ \"Error\": \"Environment variable '{KMSKEYARNNAME}' is not set.\" }}");
                return;
            }

            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };
                var requestModel = JsonSerializer.Deserialize<rsa2048_encryptRequest>(args[0], options);
                if (string.IsNullOrEmpty(requestModel.Message))
                {
                    Console.WriteLine("{\"Error\": \"Invalid JSON input. Ensure the 'Message' field is populated.\"}");
                    return;
                }

                var encryptedResponse = await EncryptMessageAsync(requestModel, kmsKeyArn);
                Console.WriteLine(JsonSerializer.Serialize(encryptedResponse));
            }
            catch (JsonException)
            {
                Console.WriteLine("{\"Error\": \"Invalid JSON format. Please provide a valid JSON input.\"}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"{{ \"Error\": \"Error encrypting message: {ex.Message}\" }}");
            }
        }

        private static async Task<rsa2048_encryptResponse> EncryptMessageAsync(rsa2048_encryptRequest request, string kmsKeyArn)
        {
            byte[] aesKey = new byte[32];
            byte[] iv = new byte[16];
            RandomNumberGenerator.Fill(aesKey);
            RandomNumberGenerator.Fill(iv);

            byte[] cipherText = AESCTREncrypt(request.Message, aesKey, iv);

            var encryptRequest = new EncryptRequest
            {
                KeyId = kmsKeyArn,
                Plaintext = new MemoryStream(aesKey),
                EncryptionAlgorithm = EncryptionAlgorithmSpec.RSAES_OAEP_SHA_256
            };

            var encryptResponse = await kmsClient.EncryptAsync(encryptRequest);
            byte[] encryptedAesKey = encryptResponse.CiphertextBlob.ToArray();

            return new rsa2048_encryptResponse
            {
                CipherText = Convert.ToBase64String(cipherText),
                EncryptedAesKey = Convert.ToBase64String(encryptedAesKey),
                Iv = Convert.ToBase64String(iv)
            };
        }

        public static byte[] AESCTREncrypt(string plaintext, byte[] key, byte[] iv)
        {
            using (Aes aes = Aes.Create())
            {
                aes.Key = key;
                aes.Mode = CipherMode.ECB;
                aes.Padding = PaddingMode.None;

                byte[] inputBytes = Encoding.UTF8.GetBytes(plaintext);
                byte[] outputBytes = new byte[inputBytes.Length];
                int blockSize = aes.BlockSize / 8;
                byte[] counter = new byte[blockSize];
                Buffer.BlockCopy(iv, 0, counter, 0, iv.Length);

                using (ICryptoTransform encryptor = aes.CreateEncryptor())
                {
                    for (int i = 0; i < inputBytes.Length; i += blockSize)
                    {
                        byte[] encryptedCounter = new byte[blockSize];
                        encryptor.TransformBlock(counter, 0, blockSize, encryptedCounter, 0);

                        for (int j = 0; j < blockSize && i + j < inputBytes.Length; j++)
                        {
                            outputBytes[i + j] = (byte)(inputBytes[i + j] ^ encryptedCounter[j]);
                        }

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
                    break;
            }
        }
    }
}
