import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

interface BKAPIGWChildStackProps extends cdk.NestedStackProps {
  filteredBenchmarkLambdas: { [key: string]: lambda.Function }
  baseAPIUrl: string,
  benchmarkRESAPIId: string,
  benchmarkRESTAPIRootResourceId: string
  architecture: string,
  language: string
}

export class ChildStackAPIGW extends cdk.NestedStack {

  public readonly createdAPIGWUrls: { [key: string]: string };
  public readonly createdMethods: apigateway.Method[];

  constructor(scope: Construct, id: string, props: BKAPIGWChildStackProps) {

    super(scope, id, props);

    this.createdAPIGWUrls = {};
    this.createdMethods = []

    const { filteredBenchmarkLambdas, baseAPIUrl, benchmarkRESAPIId, benchmarkRESTAPIRootResourceId, architecture, language } = props;

    const benchmarkRestAPI = apigateway.RestApi.fromRestApiAttributes(this, `BK-APIGW-${architecture}-${language}`, {
      restApiId: benchmarkRESAPIId,
      rootResourceId: benchmarkRESTAPIRootResourceId,
    });

    for (const [key, lambdaFunc] of Object.entries(filteredBenchmarkLambdas)) {
      // Confirm info from key
      const [architecture, sanitizedLang, operation, memorySize] = key.split('-');

      const resourceName = `${architecture}-${sanitizedLang}-${operation}-${memorySize}`;

      const resource = benchmarkRestAPI.root.addResource(resourceName);

      // Add POST method
      const method = resource.addMethod('POST', new apigateway.LambdaIntegration(lambdaFunc), {
        apiKeyRequired: true, // Optional!
        authorizationType: apigateway.AuthorizationType.NONE,
      });

      this.createdAPIGWUrls[key] = `${baseAPIUrl}/${resourceName}`;
      this.createdMethods.push(method)
    }
  }
}
