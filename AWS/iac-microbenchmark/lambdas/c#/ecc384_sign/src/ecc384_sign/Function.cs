using Amazon.Lambda.Core;
using Amazon.Lambda.APIGatewayEvents;
using System.Text.Json;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;
using Amazon;
using System.Text;

// Assembly attribute to enable the Lambda function's JSON input to be converted into .NET types
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace LambdaApiProxy
{
    // Struct representing the incoming request from body
    public struct ecc384_signRequest
    {
        public string Message { get; set; }
    }

    // Struct representing the outgoing response into body
    public struct ecc384_signResponse
    {
        public string Signature { get; set; }
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

            string KMSKEYARNNAME = "ECC384_KMS_KEY_ARN";

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
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };
                // Deserialize the incoming request body into the RequestModel struct
                var requestModel = JsonSerializer.Deserialize<ecc384_signRequest>(request.Body, options);

                // Encode the message in UTF-8
                var messageBytes = Encoding.UTF8.GetBytes(requestModel.Message);

                // Create the request for signing
                var signRequest = new SignRequest
                {
                    KeyId = KMSKEYARNVALUE,
                    Message = new MemoryStream(messageBytes),
                    MessageType = MessageType.RAW,
                    SigningAlgorithm = SigningAlgorithmSpec.ECDSA_SHA_384 // Use ECDSA_SHA_384 for P-384
                };

                var signResponse = await kmsClient.SignAsync(signRequest);

                var signature = signResponse.Signature.ToArray();

                // Encode the signature to base64 for easier transport
                var signatureB64 = Convert.ToBase64String(signature);

                // Create a response model with a message
                var responseModel = new ecc384_signResponse
                {
                    Signature = signatureB64,
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
                context.Logger.LogError($"Error processing request for ecc384_sign c#: {ex.Message}");
                var errorRsp = new Dictionary<string, string>
            {
                { "Error", $"Error processing request for ecc384_sign c#: {ex.Message}" }
            };

                APIGWResponse.StatusCode = 500;
                APIGWResponse.Body = JsonSerializer.Serialize(errorRsp);

                return APIGWResponse;
            }
        }
    }
}
