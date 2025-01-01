import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';

interface LambdaUrlStack extends cdk.NestedStackProps {
  BenchmarkLambdas: {
    [key: string]: lambda.Function
  }
  language: string,
  architecture: string
}

// This stack acts the generator for URLs for Lambdas
export class BKLambdaURLStack extends cdk.NestedStack {

  // Will be function key : url
  constructor(scope: Construct, id: string, props: LambdaUrlStack) {

    super(scope, id, props);

    const { BenchmarkLambdas, language, architecture } = props;

    // init map
    let generatedLambdaURLMap: { [key: string]: string } = {}

    // Iterate using `Object.entries`
    Object.entries(BenchmarkLambdas).forEach(([key, lambdaFunction]) => {

      // Add a Lambda Function URL with IAM authentication
      const functionUrl = lambdaFunction.addFunctionUrl({
        authType: lambda.FunctionUrlAuthType.NONE, // Use IAM auth
      });

      generatedLambdaURLMap[key] = functionUrl.url;

    });

    const aggregatedApiUrls = JSON.stringify(generatedLambdaURLMap);

    // OUTPUT FINAL URLS
    new cdk.CfnOutput(this, `AggregatedLambdaUrls-${language}-${architecture}`, {
      value: aggregatedApiUrls,
      description: `All API endpoints aggregated into a single output json string for language: ${language}, architecture: ${architecture}`,
    });

  }
}
