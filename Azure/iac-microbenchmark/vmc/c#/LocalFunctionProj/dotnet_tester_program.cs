using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace LocalFunctionProj
{
    public class dotnet_tester_program
    {
        private readonly ILogger<dotnet_tester_program> _logger;

        public dotnet_tester_program(ILogger<dotnet_tester_program> logger)
        {
            _logger = logger;
        }

        [Function("dotnet_tester_program")]
        public IActionResult Run([HttpTrigger(AuthorizationLevel.Anonymous, "get", "post")] HttpRequest req)
        {
            _logger.LogInformation("C# HTTP trigger function processed a request.");
            return new OkObjectResult("Welcome to Azure Functions!");
        }
    }
}
