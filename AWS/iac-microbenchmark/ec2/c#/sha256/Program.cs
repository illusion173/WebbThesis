using System.Text.Json;
using System.Text;
using Amazon;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;

namespace Program
{
    // Struct representing the incoming request
    public struct sha256Request
    {
        public string Message { get; set; }
    }

    // Struct representing the outgoing response
    public struct sha256Response
    {
        public string Signature { get; set; }
    }

    public class Program
    {
        private static readonly string SIGN_ALGORITHM = "HMAC_SHA_256";
        private static readonly IAmazonKeyManagementService kmsClient = new AmazonKeyManagementServiceClient(RegionEndpoint.USEast1);

        public static async Task Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("Please provide a JSON string as an argument.");
                return;
            }

            // Get the KMS key ARN from the environment variable
            string? kmsKeyArn = Environment.GetEnvironmentVariable("SHA256_KMS_KEY_ARN");
            if (string.IsNullOrEmpty(kmsKeyArn))
            {
                Console.WriteLine("Error: KMS Key ARN environment variable 'SHA256_KMS_KEY_ARN' is not set.");
                return;
            }

            // Parse JSON input from command line argument
            sha256Request request;
            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };

                request = JsonSerializer.Deserialize<sha256Request>(args[0], options);
            }
            catch (JsonException)
            {
                Console.WriteLine("Error: Invalid JSON input.");
                return;
            }

            // Proceed with signing the message using AWS KMS
            try
            {
                byte[] messageBytes = Encoding.UTF8.GetBytes(request.Message);

                var genMacResponse = await kmsClient.GenerateMacAsync(new GenerateMacRequest
                {
                    KeyId = kmsKeyArn,
                    Message = new MemoryStream(messageBytes),
                    MacAlgorithm = SIGN_ALGORITHM
                });

                // Encode the generated MAC signature in Base64
                string signatureBase64 = Convert.ToBase64String(genMacResponse.Mac.ToArray());

                // Create a response struct and print the result as JSON
                var response = new sha256Response { Signature = signatureBase64 };
                string responseJson = JsonSerializer.Serialize(response);

                Console.WriteLine(responseJson);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error signing message: {ex.Message}");
            }
        }
    }
}
