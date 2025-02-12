using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using Azure.Identity;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;

namespace Program
{
    // Struct representing the incoming request
    public struct rsa3072_encryptRequest
    {
        public string message { get; set; }
    }

    // Struct representing the outgoing response
    public struct rsa3072_encryptResponse
    {
        public string iv { get; set; }
        public string ciphertext { get; set; }
        public string encrypted_aes_key { get; set; }
    }

    public class Program
    {
        public static void Main(string[] args)
        {

            var credential = new AzureCliCredential();

            if (args.Length == 0)
            {
                Console.WriteLine("{\"Error\": \"Please provide JSON input as an argument.\"}");
                return;
            }

            string? RSA3072_KEY_NAME = Environment.GetEnvironmentVariable("RSA3072_KEY_NAME");
            string? AZURE_KEY_VAULT_URL = Environment.GetEnvironmentVariable("AZURE_KEY_VAULT_URL");

            if (string.IsNullOrEmpty(RSA3072_KEY_NAME))
            {

                Console.WriteLine($"{{ \"Error\": \"Environment variable RSA3072_KEY_NAME is not set.\" }}");
                return;
            }

            if (string.IsNullOrEmpty(AZURE_KEY_VAULT_URL))
            {
                Console.WriteLine($"{{ \"Error\": \"Environment variable  AZURE_KEY_VAULT_URL is not set.\" }}");
                return;
            }


            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };
                var requestModel = JsonSerializer.Deserialize<rsa3072_encryptRequest>(args[0], options);

                if (string.IsNullOrEmpty(requestModel.message))
                {

                    Console.WriteLine($"{{ \"Error\": \"Error serializing, message is null!\" }}");
                    return;
                }
                // Put main code here
                try
                {
                    var keyClient = new KeyClient(new Uri(AZURE_KEY_VAULT_URL), credential);

                    // Get the key from Azure Key Vault
                    KeyVaultKey key = keyClient.GetKey(RSA3072_KEY_NAME);

                    // Initialize the cryptography client for signing
                    var cryptoClient = new CryptographyClient(key.Id, credential);

                    byte[] aesKey = new byte[32];
                    byte[] iv = new byte[16];

                    RandomNumberGenerator.Fill(aesKey);
                    RandomNumberGenerator.Fill(iv);

                    byte[] cipherText = AESCTREncrypt(requestModel.message, aesKey, iv);

                    EncryptResult encryptResult = cryptoClient.Encrypt(EncryptionAlgorithm.RsaOaep256, aesKey);
                    byte[] encryptedAesKey = encryptResult.Ciphertext;

                    Console.WriteLine(JsonSerializer.Serialize(new rsa3072_encryptResponse
                    {
                        iv = Convert.ToBase64String(iv),
                        ciphertext = Convert.ToBase64String(cipherText),
                        encrypted_aes_key = Convert.ToBase64String(encryptedAesKey)
                    }));

                }
                catch (Exception ex)
                {
                    Console.WriteLine($"{{ \"Error\": \"Error doing Operation rsa3072_encrypt: {ex.Message}\" }}");
                }

            }
            catch (JsonException)
            {
                Console.WriteLine("{\"Error\": \"Invalid JSON format. Please provide a valid JSON input.\"}");
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
