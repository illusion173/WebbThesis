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

namespace dotnet_rsa3072_decrypt
{
    // Struct representing the incoming request
    public struct rsa3072_decryptRequest
    {
        public string iv { get; set; }
        public string ciphertext { get; set; }
        public string encrypted_aes_key { get; set; }
    }

    // Struct representing the outgoing response
    public struct rsa3072_decryptResponse
    {
        public string message { get; set; }
    }

    public class rsa3072_decrypt_program
    {
        private readonly ILogger<rsa3072_decrypt_program> _logger;

        public rsa3072_decrypt_program(ILogger<rsa3072_decrypt_program> logger)
        {
            _logger = logger;
        }

        [Function("dotnet_rsa3072_decrypt_program")]
        public static async Task<IActionResult> Run([HttpTrigger(AuthorizationLevel.Anonymous, "post")] HttpRequest req)
        {
            string? RSA3072_KEY_NAME = Environment.GetEnvironmentVariable("RSA3072_KEY_NAME");
            string? AZURE_KEY_VAULT_URL = Environment.GetEnvironmentVariable("AZURE_KEY_VAULT_URL");

            if (string.IsNullOrEmpty(RSA3072_KEY_NAME) || string.IsNullOrEmpty(AZURE_KEY_VAULT_URL))
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
                var requestModel = JsonSerializer.Deserialize<rsa3072_decryptRequest>(requestBodyStr, options);

                if (requestModel.ciphertext == null || requestModel.encrypted_aes_key == null || requestModel.iv == null)
                {
                    return new BadRequestObjectResult(new { error = "Invalid request payload." });
                }

                byte[] encryptedAesKey = Convert.FromBase64String(requestModel.encrypted_aes_key);
                byte[] iv = Convert.FromBase64String(requestModel.iv);
                byte[] cipherText = Convert.FromBase64String(requestModel.ciphertext);

                try
                {
                    var credential = new DefaultAzureCredential();
                    var keyClient = new KeyClient(new Uri(AZURE_KEY_VAULT_URL), credential);

                    // Get the key from Azure Key Vault
                    KeyVaultKey key = await keyClient.GetKeyAsync(RSA3072_KEY_NAME);

                    // Initialize the cryptography client for decryption
                    var cryptoClient = new CryptographyClient(key.Id, credential);
                    DecryptResult decryptResult = await cryptoClient.DecryptAsync(EncryptionAlgorithm.RsaOaep256, encryptedAesKey);
                    byte[] aesKey = decryptResult.Plaintext;

                    string decryptedMessage = AESCTRDecrypt(cipherText, aesKey, iv);

                    return new OkObjectResult(new rsa3072_decryptResponse { message = decryptedMessage });
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

        public static string AESCTRDecrypt(byte[] cipherText, byte[] key, byte[] iv)
        {
            using (Aes aes = Aes.Create())
            {
                aes.Key = key;
                aes.Mode = CipherMode.ECB;
                aes.Padding = PaddingMode.None;

                byte[] outputBytes = new byte[cipherText.Length];
                int blockSize = aes.BlockSize / 8;
                byte[] counter = new byte[blockSize];
                Buffer.BlockCopy(iv, 0, counter, 0, iv.Length);

                using (ICryptoTransform encryptor = aes.CreateEncryptor())
                {
                    for (int i = 0; i < cipherText.Length; i += blockSize)
                    {
                        byte[] encryptedCounter = new byte[blockSize];
                        encryptor.TransformBlock(counter, 0, blockSize, encryptedCounter, 0);

                        for (int j = 0; j < blockSize && i + j < cipherText.Length; j++)
                        {
                            outputBytes[i + j] = (byte)(cipherText[i + j] ^ encryptedCounter[j]);
                        }

                        IncrementCounter(counter);
                    }
                }

                return Encoding.UTF8.GetString(outputBytes).TrimEnd('\0');
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
