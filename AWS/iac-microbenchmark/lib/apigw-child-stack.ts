import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

interface ChildStackAPIGWProps extends cdk.StackProps {
  iacId: number,
  filteredBenchmarkLambdas: { [key: string]: lambda.Function }
  baseAPIUrl: string,
  benchmarkRESAPIId: string,
  benchmarkRESTAPIRootResourceId: string
}

export class ChildStackAPIGW extends cdk.Stack {

  public readonly createdAPIGWUrls: { [key: string]: string };
  public readonly createdMethods: apigateway.Method[];

  constructor(scope: Construct, id: string, props: ChildStackAPIGWProps) {

    super(scope, id, props);

    this.createdAPIGWUrls = {};
    this.createdMethods = []

    const { iacId, filteredBenchmarkLambdas, baseAPIUrl, benchmarkRESAPIId, benchmarkRESTAPIRootResourceId } = props;
    const benchmarkRestAPI = apigateway.RestApi.fromRestApiAttributes(this, `IacBenchmark-API-${iacId}`, {
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
