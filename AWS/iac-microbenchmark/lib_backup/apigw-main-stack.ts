import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as fs from 'fs';
import * as path from 'path';
import { ChildStackAPIGW } from "./apigw-child-stack"

interface MainStackAPIGWProps extends cdk.StackProps {
  iacId: number
  BenchmarkLambdas: { [key: string]: { [key: string]: lambda.Function } },
  languages: string[],
  architectures: string[],
  operations: string[],
  memorySizes: number[],
}

export class IacMainStackAPIGw extends cdk.Stack {

  constructor(scope: Construct, id: string, props: MainStackAPIGWProps) {

    super(scope, id, props);

    const { iacId, BenchmarkLambdas, languages, architectures, operations, memorySizes } = props;

    // keys should be ${architecture}-${sanitizedLang}-${operation}-${memory_size}
    // values should be the physical url to call
    let createdAPIUrls: { [key: string]: string } = {};

    const ApiGwName = `benchmarkRESTAPIGW-${iacId}`;

    const benchmarkApi = new apigateway.RestApi(this, 'benchmarkAPIGW', {
      restApiName: ApiGwName,
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key'],
        maxAge: cdk.Duration.days(1),
      },
    });

    const baseUrl = `https://${benchmarkApi.restApiId}.execute-api.${this.region}.amazonaws.com/prod`;

    // So we will create a child stack per language.
    for (const language of languages) {

      // Grab the appropriate lambda functions by language 
      // We can create new stacks by doing it by language
      let benchmarkLambdasBySpecificLanguage = BenchmarkLambdas[language];

      const apiChildStack = new ChildStackAPIGW(this, `IaCBenchMark-Child-APIGW-${language}-${iacId}`, {
        iacId: iacId,
        filteredBenchmarkLambdas: benchmarkLambdasBySpecificLanguage,
        language: language,
        architectures: architectures,
        operations: operations,
        memorySizes: memorySizes,
        baseAPIUrl: baseUrl
      });

      const createdAPIUrlsFromChild = apiChildStack.createdAPIGWUrls;

      createdAPIUrls = { ...createdAPIUrls, ...createdAPIUrlsFromChild };
    }

    const outputFilePath = path.resolve(__dirname, "../lambda_benchmark_urls.json");

    try {
      fs.writeFileSync(outputFilePath, JSON.stringify(createdAPIUrls, null, 2));
      console.log(`Endpoint URLs written to file: ${outputFilePath}`);
      console.log(createdAPIUrls);
    } catch (error) {
      console.error(`Failed to write endpoint URLs to file: ${error}`);
    }
  }
}
