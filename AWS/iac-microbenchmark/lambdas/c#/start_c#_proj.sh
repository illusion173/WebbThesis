#!/bin/bash

# Array of project directory names
projects=(
    "rsa2048_decrypt"
    "rsa2048_encrypt"
    "rsa3072_decrypt"
    "rsa3072_encrypt"
    "rsa4096_decrypt"
    "rsa4096_encrypt"
    "sha256"
    "sha384"
    "aes256_decrypt"
    "aes256_encrypt"
    "ecc256_sign"
    "ecc256_verify"
    "ecc384_sign"
    "ecc384_verify"
)

# Store the parent directory
parent_dir=$(pwd)

# Loop through each project
for project in "${projects[@]}"
do
    echo "Creating project: $project"

    # Create new Lambda project
    dotnet new lambda.EmptyFunction -n "$project"
    dotnet new console -n "$project"

    cd "$project/src/$project" || continue  # Safely change directory

    # Add necessary dependencies
    dotnet add package Amazon.Lambda.Core
    dotnet add package Amazon.Lambda.APIGatewayEvents
    dotnet add package Amazon.Lambda.Serialization.SystemTextJson
    dotnet add package AWSSDK.KeyManagementService

    # Replace Function.cs with the provided C# code
    cat <<EOL > "Function.cs"
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
EOL

# Add structs
cat <<EOL >> "Function.cs"
// Struct representing the incoming request from body
public struct ${project}Request
{
    public string Message { get; set; }
}

// Struct representing the outgoing response into body
public struct ${project}Response
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
            var requestModel = JsonSerializer.Deserialize<${project}Request>(request.Body);

            // Create a response model with a message
            var responseModel = new ${project}Response
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
            context.Logger.LogError($"Error processing request for ${project} c#: {ex.Message}");
            var errorRsp = new Dictionary<string, string>
            {
                { "Error", $"Error processing request for ${project} c#: {ex.Message}" }
            };

            APIGWResponse.StatusCode = 500;
            APIGWResponse.Body = JsonSerializer.Serialize(errorRsp);

            return APIGWResponse;
        }
    }
EOL

# Check if project is AES or RSA related
if [[ "$project" == *"aes256"* || "$project" == *"rsa"* ]]; then
    cat <<EOL >> "Function.cs"
    public static byte[] AESCTREncrypt(string plaintext, byte[] key, byte[] iv)
    {
        using (Aes aes = Aes.Create())
        {
            aes.Key = key;
            aes.IV = iv;

            // Set the mode to CTR (Counter Mode)
            aes.Mode = CipherMode.ECB; // ECB mode as a workaround, we will handle counter ourselves
            aes.Padding = PaddingMode.None; // No padding, we will handle the block size

            using (MemoryStream ms = new MemoryStream())
            {
                using (CryptoStream cs = new CryptoStream(ms, aes.CreateEncryptor(), CryptoStreamMode.Write))
                {
                    // Convert plaintext to byte array
                    byte[] inputBytes = System.Text.Encoding.UTF8.GetBytes(plaintext);

                    // AES block size
                    int blockSize = aes.BlockSize / 8; // BlockSize is in bits, convert to bytes

                    // Counter initialization
                    byte[] counter = new byte[blockSize];
                    Buffer.BlockCopy(iv, 0, counter, 0, blockSize);

                    // Encrypt using CTR mode
                    for (int i = 0; i < inputBytes.Length; i++)
                    {
                        if (i % blockSize == 0 && i != 0) // Increment counter after each block
                        {
                            IncrementCounter(counter);
                        }

                        byte[] block = new byte[1] { inputBytes[i] };
                        cs.Write(block, 0, block.Length);
                        cs.WriteByte((byte)(block[0] ^ counter[i % blockSize])); // XOR with the counter
                    }
                }

                return ms.ToArray();
            }
        }
    }

    public static string AESCTRDecrypt(byte[] ciphertext, byte[] key, byte[] iv)
    {
        using (Aes aes = Aes.Create())
        {
            aes.Key = key;

            // Set the mode to ECB
            aes.Mode = CipherMode.ECB; // ECB mode as a workaround, we will handle counter ourselves
            aes.Padding = PaddingMode.None; // No padding, we will handle the block size

            using (MemoryStream ms = new MemoryStream())
            {
                // AES block size
                int blockSize = aes.BlockSize / 8; // BlockSize is in bits, convert to bytes

                // Counter initialization
                byte[] counter = new byte[blockSize];
                Buffer.BlockCopy(iv, 0, counter, 0, blockSize);

                // Decrypt using CTR mode
                for (int i = 0; i < ciphertext.Length; i++)
                {
                    if (i % blockSize == 0 && i != 0) // Increment counter after each block
                    {
                        IncrementCounter(counter);
                    }

                    byte[] block = new byte[1] { ciphertext[i] };
                    byte decryptedByte = (byte)(block[0] ^ counter[i % blockSize]); // XOR with the counter
                    ms.WriteByte(decryptedByte);
                }

                return System.Text.Encoding.UTF8.GetString(ms.ToArray());
            }
        }
    }

    private static void IncrementCounter(byte[] counter)
    {
        for (int i = counter.Length - 1; i >= 0; i--)
        {
            if (++counter[i] != 0)
                break; // If no overflow, we are done
        }
    }
EOL
fi

# Close the namespace block
cat <<EOL >> "Function.cs"
}
}
EOL
    cd "$parent_dir" || exit 1  # Ensure you return to the parent directory
    echo "Project $project created and dependencies added."
done

echo "All projects created."
