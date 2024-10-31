using System.Text;
using System.Text.Json;
using Amazon;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;

namespace Program
{
    // Struct representing the incoming request from JSON input
    public struct ecc256_signRequest
    {
        public string Message { get; set; }
    }

    // Struct representing the outgoing response to be displayed
    public struct ecc256_signResponse
    {
        public string Signature { get; set; }
    }

    public class Program
    {
        private static readonly IAmazonKeyManagementService kmsClient = new AmazonKeyManagementServiceClient(RegionEndpoint.USEast1);

        public static async Task Main(string[] args)
        {
            // Ensure input is provided as an argument
            if (args.Length == 0)
            {
                Console.WriteLine("{ \"Error\": \"Please provide JSON input as an argument.\" }");
                return;
            }

            // Get the KMS Key ARN from the environment variable
            string KMSKEYARNNAME = "ECC256_KMS_KEY_ARN";
            string? KMSKEYARNVALUE = Environment.GetEnvironmentVariable(KMSKEYARNNAME);

            if (string.IsNullOrEmpty(KMSKEYARNVALUE))
            {
                Console.WriteLine($"{{ \"Error\": \"Environment variable '{KMSKEYARNNAME}' is not set.\" }}");
                return;
            }

            try
            {
                // Parse JSON input from the argument
                var requestModel = JsonSerializer.Deserialize<ecc256_signRequest>(args[0]);
                if (string.IsNullOrEmpty(requestModel.Message))
                {
                    Console.WriteLine("{ \"Error\": \"Invalid JSON input. Please provide a valid JSON with 'Message' field.\" }");
                    return;
                }

                // Sign the message
                var signResponse = await SignMessageAsync(requestModel, KMSKEYARNVALUE);

                // Output the result as JSON
                Console.WriteLine(JsonSerializer.Serialize(signResponse));
            }
            catch (JsonException)
            {
                Console.WriteLine("{ \"Error\": \"Invalid JSON format. Please provide a valid JSON input.\" }");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"{{ \"Error\": \"Error signing message: {ex.Message}\" }}");
            }
        }

        private static async Task<ecc256_signResponse> SignMessageAsync(ecc256_signRequest request, string kmsKeyArn)
        {
            var messageBytes = Encoding.UTF8.GetBytes(request.Message);

            // Create the request for signing
            var signRequest = new SignRequest
            {
                KeyId = kmsKeyArn,
                Message = new MemoryStream(messageBytes),
                MessageType = MessageType.RAW,
                SigningAlgorithm = SigningAlgorithmSpec.ECDSA_SHA_256
            };

            // Call KMS to sign the message
            var signResponse = await kmsClient.SignAsync(signRequest);
            var signature = signResponse.Signature.ToArray();

            // Encode the signature to base64
            var signatureB64 = Convert.ToBase64String(signature);

            return new ecc256_signResponse
            {
                Signature = signatureB64
            };
        }
    }
}
