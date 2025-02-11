#!/bin/bash

# Array of project directory names
projects=(
    "rsa2048_decrypt"
    "rsa2048_encrypt"
    "rsa3072_decrypt"
    "rsa3072_encrypt"
    "rsa4096_decrypt"
    "rsa4096_encrypt"
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

    # Create new project
    dotnet new console -n "$project"

    cd "$project" || continue  # Safely change directory
    # Add necessary dependencies
    dotnet add package Microsoft.Extensions.Azure
    dotnet add package Azure.Identity --version 1.13.2
    dotnet add package Azure.Security.KeyVault.Keys --version 4.7.0
    rm Program.cs

    cat <<EOL > Program.cs
using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using Azure;
using Azure.Core;
using Azure.Identity;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;

namespace Program
{
    // Struct representing the incoming request
    public struct ${project}Request
    {
        public string Message { get; set; }
    }

    // Struct representing the outgoing response
    public struct ${project}Response
    {

        public string Message { get; set; }
    }

    public class Program
    {
        public static async Task Main(string[] args)
        {

            var credential = new AzureCliCredential();

            if (args.Length == 0)
            {
                Console.WriteLine("{\"Error\": \"Please provide JSON input as an argument.\"}");
                return;
            }

            string? _KEY_NAME = Environment.GetEnvironmentVariable("_KEY_NAME");
            string? AZURE_KEY_VAULT_URL = Environment.GetEnvironmentVariable("AZURE_KEY_VAULT_URL");

            if (string.IsNullOrEmpty(_KEY_NAME))
            {
                Console.WriteLine($"{{ \"Error\": \"Environment variable '{_KEY_NAME}' is not set.\" }}");
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
                var requestModel = JsonSerializer.Deserialize<${project}Request>(args[0], options);


                // Put main code here
                try
                {
                    var keyClient = new KeyClient(new Uri(AZURE_KEY_VAULT_URL), credential);

                    // Get the key from Azure Key Vault
                    KeyVaultKey key = keyClient.GetKey(_KEY_NAME);

                    // Initialize the cryptography client for signing
                    var cryptoClient = new CryptographyClient(key.Id, credential);

                }
                catch (Exception ex)
                {
                   Console.WriteLine($"{{ \"Error\": \"Error doing Operation ${project}: {ex.Message}\" }}");
                }

                Console.WriteLine(JsonSerializer.Serialize(new ${project}Response { Message = plaintextMessage }));
            }
            catch (JsonException)
            {
                Console.WriteLine("{\"Error\": \"Invalid JSON format. Please provide a valid JSON input.\"}");
            }
        }

    }

}
EOL

    cd "$parent_dir" || exit 1  # Ensure you return to the parent directory
    echo "Project $project created and dependencies added."
done

echo "All projects created."
