import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as fs from 'fs';
import * as path from 'path';
import { ChildStackAPIGW } from "./apigw-child-stack"
import { DeployStack } from "./apigw-deployment-stack"
interface MainStackAPIGWProps extends cdk.StackProps {
  iacId: number
  BenchmarkLambdas: {
    [key: string]: { [key: string]: { [key: string]: lambda.Function } }
  },
  languages: string[],
  architectures: string[],
}

export class IacMainStackAPIGw extends cdk.Stack {

  constructor(scope: Construct, id: string, props: MainStackAPIGWProps) {

    super(scope, id, props);

    const { iacId, BenchmarkLambdas, languages, architectures, } = props;

    // keys should be ${architecture}-${sanitizedLang}-${operation}-${memory_size}
    // values should be the physical url to call
    let createdAPIUrls: { [key: string]: string } = {};

    // Where the methods will exist for the API.
    let createdAPIMethods: apigateway.Method[] = []

    const ApiGwName = `benchmarkRESTAPIGW-${iacId}`;


    const benchmarkApi = new apigateway.RestApi(this, `IacBenchmark-API-${iacId}`, {
      restApiName: ApiGwName,
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key'],
        maxAge: cdk.Duration.days(1),
      },
      deploy: true,
    });

    // Avoid some issues with not being to do POST, just in case.
    benchmarkApi.root.addMethod('ANY');

    const benchmarkRESAPIId: string = benchmarkApi.restApiId;

    const benchmarkRESTApiRootResourceId: string = benchmarkApi.restApiRootResourceId;

    const baseUrl = `https://${benchmarkApi.restApiId}.execute-api.${this.region}.amazonaws.com/prod`;
    let child_num = 1;

    // So we will create a child stack per language and architecture to avoid hitting stack limits, currently 500 resources can be created per stack.
    for (const architecture of architectures) {

      for (const language of languages) {

        // Grab the appropriate lambda functions by language & architecture
        let benchmarkLambdasBySpecificLanguageArch = BenchmarkLambdas[language][architecture];

        const apiChildStack = new ChildStackAPIGW(this, `IaCBenchMark-Child-APIGW-${language}-${architecture}-${iacId}-${child_num}`, {
          iacId: iacId,
          filteredBenchmarkLambdas: benchmarkLambdasBySpecificLanguageArch,
          baseAPIUrl: baseUrl,
          benchmarkRESAPIId: benchmarkRESAPIId,
          benchmarkRESTAPIRootResourceId: benchmarkRESTApiRootResourceId
        });
        //
        //language, architecture, operations, memorySizes,

        const createdAPIUrlsFromChild = apiChildStack.createdAPIGWUrls;
        const createdMethodsFromChild = apiChildStack.createdMethods;

        // Combine with already created data
        createdAPIUrls = { ...createdAPIUrls, ...createdAPIUrlsFromChild };

        createdAPIMethods = { ...createdAPIMethods, ...createdMethodsFromChild };

        child_num += 1;
      }
    }


    // output the urls via cf outputs check generate_urls.js for how the information is grabbed.
    for (const [key, url] of Object.entries(createdAPIUrls)) {
      new cdk.CfnOutput(this, `${key}`, {
        value: url,
        description: `API endpoint for ${key}`,
      });
    }

    // Deploy the API!
    new DeployStack(this, `IaCBenchMark-APIGW-Deployment-${iacId}`, {
      restApiId: benchmarkRESAPIId,
      benchmarkMethods: createdAPIMethods,
      iacId: iacId
    });

  }
}
