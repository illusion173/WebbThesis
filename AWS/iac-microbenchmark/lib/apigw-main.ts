import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { ChildStackAPIGW } from "./apigw-child";


interface BKAPIGWStackProps extends cdk.NestedStackProps {
  BenchmarkLambdas: {
    [key: string]: { [key: string]: { [key: string]: lambda.Function } }
  },
  languages: string[],
  architectures: string[],
}




export class BKAPIGWStackMain extends cdk.NestedStack {

  constructor(scope: Construct, id: string, props: BKAPIGWStackProps) {
    super(scope, id, props);
    interface ApiInfo {
      api_key: string;
      api_urls: { [key: string]: string };
    }
    const { BenchmarkLambdas, languages, architectures, } = props;

    interface ApiInfo {
      api_key: string;
      api_urls: { [key: string]: string };
    }
    // In order to have an efficient way to access the urls with an API Key we must define the structure
    let apiGWInformationOutputCfn: ApiInfo[] = [];
    // each architecture & language will have its own api. each api will have its own api key with urls
    // Create a list with each {} contains apikey (string: string), with the key lookup with corresponding urls
    // 
    /*
    [
      {
      api_key: string
      api_urls: {lambdakey: url}
      }
    ]

      */

    let apiDeployInfo: { [key: string]: apigateway.Method[] } = {}

    let createdAPIUrls: { [key: string]: string } = {};

    for (const architecture of architectures) {

      for (const language of languages) {

        // Should be all unique.
        const apiGWName = `benchmarkAPI-${architecture}-${language}`

        const benchmarkApi = new apigateway.RestApi(this, `BK-APIGW-${architecture}-${language}`, {
          restApiName: apiGWName,
          defaultCorsPreflightOptions: {
            allowOrigins: apigateway.Cors.ALL_ORIGINS,
            allowMethods: apigateway.Cors.ALL_METHODS,
            allowHeaders: ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key'],
            maxAge: cdk.Duration.days(1),
          },
          deploy: false,
        })

        // Add an API Key
        const apiKey = new apigateway.ApiKey(this, `BK-APIKey-${architecture}-${language}`, {
          apiKeyName: `BKAPIKey-${architecture}-${language}`,
        });
        // Add a Usage Plan without limits
        const usagePlan = new apigateway.UsagePlan(this, `BenchmarkUsagePlan-${architecture}-${language}`, {
          name: `BKUsagePlan-${architecture}-${language}`,
          // No throttle or quota settings, unlimited usage
        });

        // Associate the API Key with the Usage Plan
        usagePlan.addApiKey(apiKey);


        // Avoid some issues with not being to do POST, just in case.
        benchmarkApi.root.addMethod('ANY');

        const benchmarkRESAPIId: string = benchmarkApi.restApiId;

        // This will be used for api deployment as a key containing info about the API's name
        const restAPIIDComplete: string = `${benchmarkRESAPIId}-${architecture}-${language}`;

        const benchmarkRESTApiRootResourceId: string = benchmarkApi.restApiRootResourceId;

        const baseUrl = `https://${benchmarkApi.restApiId}.execute-api.${this.region}.amazonaws.com/prod`;

        // Grab the appropriate lambda functions by language & architecture
        let benchmarkLambdasBySpecificLanguageArch = BenchmarkLambdas[language][architecture];

        const apiChildStack = new ChildStackAPIGW(this, `IaCBenchMark-Child-APIGW-${language}-${architecture}`, {
          filteredBenchmarkLambdas: benchmarkLambdasBySpecificLanguageArch,
          baseAPIUrl: baseUrl,
          benchmarkRESAPIId: benchmarkRESAPIId,
          benchmarkRESTAPIRootResourceId: benchmarkRESTApiRootResourceId,
          architecture: architecture,
          language: language
        });

        const createdAPIUrlsFromChild = apiChildStack.createdAPIGWUrls;

        const createdMethodsFromChild = apiChildStack.createdMethods;

        // Combine with already created data
        // This will be the physical urls that we need to ping for benchmarking
        createdAPIUrls = { ...createdAPIUrls, ...createdAPIUrlsFromChild };

        // Add the API info
        // requires manual intervention for user to input their own api keys, check aws cli or console to view them.

        let cfnOutputForAPI: ApiInfo = {
          api_key: "INSERTAPIKEYHERE",
          api_urls: createdAPIUrls,
        };

        // Add methods to the benchmark api's map for deployment
        apiDeployInfo[restAPIIDComplete] = createdMethodsFromChild;

        // Push the API info onto the list.
        apiGWInformationOutputCfn.push(cfnOutputForAPI);

      }
    }


    // Convert to a json string
    const aggregatedApiUrls = JSON.stringify(apiGWInformationOutputCfn);

    new cdk.CfnOutput(this, 'AggregatedAPIUrls', {
      value: aggregatedApiUrls,
      description: 'All API endpoints and keys aggregated into a single output json string',
    });


    /*
 
     for (const [benchmarkRESAPIIdComplete, createdAPIMethods] of Object.entries(apiDeployInfo)) {
       const [benchmarkRESAPIId, architecture, language, iacId] = benchmarkRESAPIIdComplete.split("-");
       // Deploy the APIs!
       new DeployStack(this, `IaCBenchMark-APIGW-Deployment-${architecture}-${language}-${iacId}`, {
         restApiId: benchmarkRESAPIId,
         benchmarkMethods: createdAPIMethods,
         iacId: iacId,
         architecture: architecture,
         language: language,
       });
 
     }

    */
  }
}
