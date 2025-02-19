using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using Azure.Identity;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;

namespace dotnet_rsa2048_encrypt
{
    // Struct representing the incoming request
    public struct rsa2048_encryptRequest
    {
        public string message { get; set; }
    }

    // Struct representing the outgoing response
    public struct rsa2048_encryptResponse
    {
        public string iv { get; set; }
        public string ciphertext { get; set; }
        public string encrypted_aes_key { get; set; }
    }

    public class rsa2048_encrypt_program
    {
        private readonly ILogger<rsa2048_encrypt_program> _logger;

        public rsa2048_encrypt_program(ILogger<rsa2048_encrypt_program> logger)
        {
            _logger = logger;
        }

        [Function("dotnet_rsa2048_encrypt_program")]
        public static async Task<IActionResult> Run([HttpTrigger(AuthorizationLevel.Anonymous, "post")] HttpRequest req)
        {
            string? RSA2048_KEY_NAME = Environment.GetEnvironmentVariable("RSA2048_KEY_NAME");
            string? AZURE_KEY_VAULT_URL = Environment.GetEnvironmentVariable("AZURE_KEY_VAULT_URL");

            if (string.IsNullOrEmpty(RSA2048_KEY_NAME) || string.IsNullOrEmpty(AZURE_KEY_VAULT_URL))
            {
                return new BadRequestObjectResult(new { error = "Environment variables may be missing." });
            }

            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };

                string requestBodyStr = await new StreamReader(req.Body).ReadToEndAsync();
                var requestModel = JsonSerializer.Deserialize<rsa2048_encryptRequest>(requestBodyStr, options);

                if (requestModel.message == null)
                {
                    return new BadRequestObjectResult(new { error = "Invalid request payload." });
                }

                // Generate AES key and IV
                byte[] aesKey = new byte[32];
                byte[] iv = new byte[16];
                RandomNumberGenerator.Fill(aesKey);
                RandomNumberGenerator.Fill(iv);

                byte[] cipherText = AESCTREncrypt(requestModel.message, aesKey, iv);

                try
                {
                    var credential = new DefaultAzureCredential();
                    var keyClient = new KeyClient(new Uri(AZURE_KEY_VAULT_URL), credential);

                    // Get the key from Azure Key Vault
                    KeyVaultKey key = await keyClient.GetKeyAsync(RSA2048_KEY_NAME);

                    // Initialize the cryptography client for encryption
                    var cryptoClient = new CryptographyClient(key.Id, credential);
                    EncryptResult encryptResult = await cryptoClient.EncryptAsync(EncryptionAlgorithm.RsaOaep256, aesKey);
                    byte[] encryptedAesKey = encryptResult.Ciphertext;

                    return new OkObjectResult(new rsa2048_encryptResponse
                    {
                        iv = Convert.ToBase64String(iv),
                        ciphertext = Convert.ToBase64String(cipherText),
                        encrypted_aes_key = Convert.ToBase64String(encryptedAesKey)
                    });
                }
                catch (Exception ex)
                {
                    return new BadRequestObjectResult(new { error = ex.Message });
                }
            }
            catch (JsonException)
            {
                return new BadRequestObjectResult(new { error = "Invalid JSON payload." });
            }
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
