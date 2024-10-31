using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using Amazon;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;

namespace Program
{
    // Struct representing the incoming request
    public struct rsa2048_decryptRequest
    {
        public string CipherText { get; set; }
        public string Iv { get; set; }
        public string EncryptedAesKey { get; set; }
    }

    // Struct representing the outgoing response
    public struct rsa2048_decryptResponse
    {
        public string Message { get; set; }
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
                var requestModel = JsonSerializer.Deserialize<rsa2048_decryptRequest>(args[0]);
                if (string.IsNullOrEmpty(requestModel.CipherText) || string.IsNullOrEmpty(requestModel.Iv) || string.IsNullOrEmpty(requestModel.EncryptedAesKey))
                {
                    Console.WriteLine("{\"Error\": \"Invalid JSON input. Ensure all fields are populated.\"}");
                    return;
                }

                var plaintextMessage = await DecryptMessageAsync(requestModel, kmsKeyArn);
                Console.WriteLine(JsonSerializer.Serialize(new rsa2048_decryptResponse { Message = plaintextMessage }));
            }
            catch (JsonException)
            {
                Console.WriteLine("{\"Error\": \"Invalid JSON format. Please provide a valid JSON input.\"}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"{{ \"Error\": \"Error decrypting message: {ex.Message}\" }}");
            }
        }

        private static async Task<string> DecryptMessageAsync(rsa2048_decryptRequest request, string kmsKeyArn)
        {
            byte[] iv = Convert.FromBase64String(request.Iv);
            byte[] encryptedAesKey = Convert.FromBase64String(request.EncryptedAesKey);
            byte[] cipherText = Convert.FromBase64String(request.CipherText);

            var decryptRequest = new DecryptRequest
            {
                CiphertextBlob = new MemoryStream(encryptedAesKey),
                KeyId = kmsKeyArn,
                EncryptionAlgorithm = EncryptionAlgorithmSpec.RSAES_OAEP_SHA_256
            };

            var decryptResponse = await kmsClient.DecryptAsync(decryptRequest);
            byte[] decryptedAesKey = decryptResponse.Plaintext.ToArray();

            return Encoding.UTF8.GetString(AESCTRDecrypt(cipherText, decryptedAesKey, iv));
        }

        public static byte[] AESCTRDecrypt(byte[] ciphertext, byte[] key, byte[] iv)
        {
            using (Aes aes = Aes.Create())
            {
                aes.Key = key;
                aes.Mode = CipherMode.ECB;
                aes.Padding = PaddingMode.None;

                int blockSize = aes.BlockSize / 8;
                byte[] counter = new byte[blockSize];
                Buffer.BlockCopy(iv, 0, counter, 0, iv.Length);

                byte[] outputBytes = new byte[ciphertext.Length];
                using (ICryptoTransform encryptor = aes.CreateEncryptor())
                {
                    for (int i = 0; i < ciphertext.Length; i += blockSize)
                    {
                        byte[] encryptedCounter = new byte[blockSize];
                        encryptor.TransformBlock(counter, 0, blockSize, encryptedCounter, 0);

                        for (int j = 0; j < blockSize && i + j < ciphertext.Length; j++)
                        {
                            outputBytes[i + j] = (byte)(ciphertext[i + j] ^ encryptedCounter[j]);
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
