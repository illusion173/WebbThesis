using System.Text;
using System.Text.Json;
using Amazon;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;

namespace Program
{
    // Struct representing the incoming request
    public struct ecc256_verifyRequest
    {
        public string Signature { get; set; }
        public string Message { get; set; }
    }

    // Struct representing the outgoing response
    public struct ecc256_verifyResponse
    {
        public bool IsValid { get; set; }
    }

    public class Program
    {
        private static readonly IAmazonKeyManagementService kmsClient = new AmazonKeyManagementServiceClient(RegionEndpoint.USEast1);

        public static async Task Main(string[] args)
        {
            // Check for JSON input argument
            if (args.Length == 0)
            {
                Console.WriteLine("{ \"Error\": \"Please provide JSON input as an argument.\" }");
                return;
            }

            // Get the KMS Key ARN from the environment variable
            string KMSKEYARNNAME = "ECC256_KMS_KEY_ARN";
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
                // Parse JSON input from argument
                var requestModel = JsonSerializer.Deserialize<ecc256_verifyRequest>(args[0], options);
                if (string.IsNullOrEmpty(requestModel.Signature) || string.IsNullOrEmpty(requestModel.Message))
                {
                    Console.WriteLine("{ \"Error\": \"Invalid JSON input. Please provide a valid JSON with 'Signature' and 'Message' fields.\" }");
                    return;
                }

                // Verify the signature
                var verifyResponse = await VerifySignatureAsync(requestModel, kmsKeyArn);

                // Output the result as JSON
                Console.WriteLine(JsonSerializer.Serialize(verifyResponse));
            }
            catch (JsonException)
            {
                Console.WriteLine("{ \"Error\": \"Invalid JSON format. Please provide a valid JSON input.\" }");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"{{ \"Error\": \"Error verifying signature: {ex.Message}\" }}");
            }
        }

        private static async Task<ecc256_verifyResponse> VerifySignatureAsync(ecc256_verifyRequest request, string kmsKeyArn)
        {
            // Decode Base64-encoded signature and encode the message in UTF-8
            var signatureBytes = Convert.FromBase64String(request.Signature);
            var messageBytes = Encoding.UTF8.GetBytes(request.Message);

            // Create the request for verifying the signature
            var verifyRequest = new VerifyRequest
            {
                KeyId = kmsKeyArn,
                Message = new MemoryStream(messageBytes),
                MessageType = MessageType.RAW,
                Signature = new MemoryStream(signatureBytes),
                SigningAlgorithm = SigningAlgorithmSpec.ECDSA_SHA_256
            };

            // Call KMS to verify the signature
            var verifyResponse = await kmsClient.VerifyAsync(verifyRequest);

            // Return the verification result
            return new ecc256_verifyResponse
            {
                IsValid = verifyResponse.SignatureValid
            };
        }
    }
}
