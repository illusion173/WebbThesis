#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

for PROJECT in "${PROJECTS[@]}"; do

    echo "Setting up project: $PROJECT"
    func init dotnet_$PROJECT --worker-runtime dotnet-isolated --target-framework net8.0
    cd dotnet_$PROJECT
    rm host.json
    rm Program.cs

    rm dotnet_${PROJECT}.csproj

    cat <<EOF > dotnet_${PROJECT}.csproj
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <AzureFunctionsVersion>v4</AzureFunctionsVersion>
    <OutputType>Exe</OutputType>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <PublishReadyToRun>true</PublishReadyToRun>
  </PropertyGroup>
  <ItemGroup>
    <FrameworkReference Include="Microsoft.AspNetCore.App" />
    <PackageReference Include="Azure.Identity" Version="1.13.2" />
    <PackageReference Include="Azure.Security.KeyVault.Keys" Version="4.7.0" />
    <PackageReference Include="Microsoft.ApplicationInsights.WorkerService" Version="2.22.0" />
    <!-- Application Insights isn't enabled by default. See https://aka.ms/AAt8mw4. -->
    <!-- <PackageReference Include="Microsoft.ApplicationInsights.WorkerService" Version="2.22.0" /> -->
    <!-- <PackageReference Include="Microsoft.Azure.Functions.Worker.ApplicationInsights" Version="2.0.0" /> -->
    <PackageReference Include="Microsoft.Azure.Functions.Worker" Version="2.0.0" />
    <PackageReference Include="Microsoft.Azure.Functions.Worker.ApplicationInsights" Version="2.0.0" />
    <PackageReference Include="Microsoft.Azure.Functions.Worker.Extensions.Http" Version="3.2.0" />
    <PackageReference Include="Microsoft.Azure.Functions.Worker.Extensions.Http.AspNetCore" Version="2.0.0" />
    <PackageReference Include="Microsoft.Azure.Functions.Worker.Sdk" Version="2.0.0" />
    <PackageReference Include="Microsoft.Extensions.Azure" Version="1.10.0" />
  </ItemGroup>
  <ItemGroup>
    <None Update="host.json">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </None>
    <None Update="local.settings.json">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
      <CopyToPublishDirectory>Never</CopyToPublishDirectory>
    </None>
  </ItemGroup>
  <ItemGroup>
    <Using Include="System.Threading.ExecutionContext" Alias="ExecutionContext" />
  </ItemGroup>
</Project>
EOF

    cat <<EOF > host.json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.*, 4.0.0)"
  }
}
EOF

    func new --template "HTTP trigger" --authlevel "anonymous" --name "${PROJECT}_program"

    rm ${PROJECT}_program.cs

    cat <<EOF > ${PROJECT}_program.cs
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

namespace dotnet_$PROJECT
{

    // Struct representing the incoming request
    public struct ${PROJECT}Request
    {
        public string Message { get; set; }
    }

    // Struct representing the outgoing response
    public struct ${PROJECT}Response
    {
        public string Message { get; set; }
    }

    public class ${PROJECT}_program
    {
        private readonly ILogger<${PROJECT}_program> _logger;

        public ${PROJECT}_program(ILogger<${PROJECT}_program> logger)
        {
            _logger = logger;
        }

        [Function("${PROJECT}_program")]
        public IActionResult Run([HttpTrigger(AuthorizationLevel.Anonymous,"post")] HttpRequest req)
        {
            string? _KEY_NAME = Environment.GetEnvironmentVariable("_KEY_NAME");
            string? AZURE_KEY_VAULT_URL = Environment.GetEnvironmentVariable("AZURE_KEY_VAULT_URL");


            if (string.IsNullOrEmpty(_KEY_NAME) || string.IsNullOrEmpty(AZURE_KEY_VAULT_URL))
            {
                return new BadRequestResult();
            }

            try
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true // Enable case-insensitive deserialization
                };


                string requestBodyStr =  new StreamReader(req.Body).ReadToEnd();
                var requestModel = JsonSerializer.Deserialize<ecc256_signRequest>(requestBodyStr, options);

                // Convert hex string to byte array
                byte[] messageDigestBytes;
                try
                {
                    messageDigestBytes = Convert.FromHexString(requestModel.message_digest);
                }
                catch (FormatException)
                {
                    return new BadRequestResult();
                }

                // Put main code here
                try
                {

                    var credential = new DefaultAzureCredential();
                    var keyClient = new KeyClient(new Uri(AZURE_KEY_VAULT_URL), credential);

                    // Get the key from Azure Key Vault
                    KeyVaultKey key = keyClient.GetKey(_KEY_NAME);

                    // Initialize the cryptography client for signing
                    var cryptoClient = new CryptographyClient(key.Id, credential);

                    return new OkObjectResult(JsonSerializer.Serialize(new ${PROJECT}Response {  }));

                }
                catch (Exception ex)
                {

                    return new BadRequestObjectResult(new { error = ex.Message });
                }

            }
            catch (JsonException)
            {
            
                return new BadRequestResult();
            }
        }
    }
}
EOF
    echo "Adding dependencies"

    # Add necessary dependencies
    dotnet add package Microsoft.Extensions.Azure
    dotnet add package Azure.Identity --version 1.13.2
    dotnet add package Azure.Security.KeyVault.Keys --version 4.7.0
    dotnet add package Microsoft.ApplicationInsights.WorkerService
    dotnet add package Microsoft.Azure.Functions.Worker.ApplicationInsights
    echo "Finished ${PROJECT}"
    cd ..

done

echo "Finished Preparing dotnet 8 projects."
