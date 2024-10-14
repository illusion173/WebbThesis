using Amazon.Lambda.Core;
using Amazon.Lambda.APIGatewayEvents;
using System.Text.Json;
using System.Collections.Generic;
using System;
using System.Security.Cryptography;
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;
using Amazon;

// Assembly attribute to enable the Lambda function's JSON input to be converted into .NET types
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace LambdaApiProxy
{
  // Struct representing the incoming request from body
  public struct sha256Request
  {
    public string Message { get; set; }
  }

  // Struct representing the outgoing response into body
  public struct sha256Response
  {
    public string ResponseMessage { get; set; }
  }

  public class Function
  {
    // The Lambda handler function
    public APIGatewayProxyResponse FunctionHandler(APIGatewayProxyRequest request, ILambdaContext context)
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


      string KMSKEYARNNAME = "_KMS_KEY_ARN";

      // Get the value of the environment variable
      string KMSKEYARNVALUE = Environment.GetEnvironmentVariable(KMSKEYARNNAME);

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
        // Deserialize the incoming request body into the RequestModel struct
        var requestModel = JsonSerializer.Deserialize<sha256Request>(request.Body);

        // Create a response model with a message
        var responseModel = new sha256Response
        {
          ResponseMessage = $"Hello, {requestModel.Message}!",
        };


        var region = RegionEndpoint.USEast1;

        // Create the KMS client
        using var kmsClient = new AmazonKeyManagementServiceClient(region);

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
        context.Logger.LogError($"Error processing request for sha256 c#: {ex.Message}");
        var errorRsp = new Dictionary<string, string>
            {
                { "Error", $"Error processing request for sha256 c#: {ex.Message}" }
            };

        APIGWResponse.StatusCode = 500;
        APIGWResponse.Body = JsonSerializer.Serialize(errorRsp);

        return APIGWResponse;
      }
    }
  }
}
