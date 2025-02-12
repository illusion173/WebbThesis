using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using Azure.Identity;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;

namespace Program
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
                Console.WriteLine("{ \"Error\": \"Environment variable RSA3072_KEY_NAME is not set.\" }");
                return;
            }

            if (string.IsNullOrEmpty(AZURE_KEY_VAULT_URL))
            {
                Console.WriteLine("{ \"Error\": \"Environment variable AZURE_KEY_VAULT_URL is not set.\" }");
                return;
            }

            try
            {
                var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                var requestModel = JsonSerializer.Deserialize<rsa3072_decryptRequest>(args[0], options);

                if (string.IsNullOrEmpty(requestModel.iv) ||
                    string.IsNullOrEmpty(requestModel.ciphertext) ||
                    string.IsNullOrEmpty(requestModel.encrypted_aes_key))
                {
                    Console.WriteLine("{\"Error\": \"Invalid input JSON. Required fields are missing.\"}");
                    return;
                }

                try
                {
                    var keyClient = new KeyClient(new Uri(AZURE_KEY_VAULT_URL), credential);
                    KeyVaultKey key = keyClient.GetKey(RSA3072_KEY_NAME);
                    var cryptoClient = new CryptographyClient(key.Id, credential);

                    byte[] encryptedAesKey = Convert.FromBase64String(requestModel.encrypted_aes_key);
                    DecryptResult decryptResult = cryptoClient.Decrypt(EncryptionAlgorithm.RsaOaep256, encryptedAesKey);
                    byte[] aesKey = decryptResult.Plaintext;

                    byte[] iv = Convert.FromBase64String(requestModel.iv);
                    byte[] cipherText = Convert.FromBase64String(requestModel.ciphertext);

                    string decryptedMessage = AESCTRDecrypt(cipherText, aesKey, iv);

                    Console.WriteLine(JsonSerializer.Serialize(new rsa3072_decryptResponse { message = decryptedMessage }));
                }
                catch (Exception ex)
                {
                    Console.WriteLine("{\"Error\": \"Error doing Operation rsa3072_decrypt: " + ex.Message + "\"}");
                }
            }
            catch (JsonException)
            {
                Console.WriteLine("{\"Error\": \"Invalid JSON format. Please provide a valid JSON input.\"}");
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
