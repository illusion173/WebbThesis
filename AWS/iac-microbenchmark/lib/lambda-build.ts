import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import path from 'path';
import { BKLambdaURLStack } from "./lambda-urls"
interface BKLambdaChildProps extends cdk.StackProps {
  language: string,
  architecture: string,
  operations: string[],
  memorySizes: number[],
  kmsKeyEnvs: { [key: string]: { [key: string]: string } },
  kmsKeyARNList: string[]
}

export class BKLambdaBuildStack extends cdk.Stack {

  // (function key is `${architecture}-${sanitizedLang}-${operation}-${memorySize}`)

  constructor(scope: Construct, id: string, props: BKLambdaChildProps) {

    super(scope, id, props);
    let createdChildLambdas: { [key: string]: lambda.Function } = {}

    const { language, architecture, operations, memorySizes, kmsKeyEnvs, kmsKeyARNList } = props;


    const logLambdaPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
      ],
      resources: ["*"],
    }
    );

    const enableKeyAccessPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'kms:Encrypt',
        'kms:Decrypt',
        'kms:GenerateDataKey',
        'kms:GenerateDataKeyWithoutPlaintext',
        'kms:DescribeKey',
        'kms:Sign',
        'kms:Verify',
        'kms:GenerateMac'
      ],
      resources: kmsKeyARNList
    });

    const lambdaRoleName: string = "BKLambdaRole";

    let BenchmarkLambdaRole = new iam.Role(this, lambdaRoleName, {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    BenchmarkLambdaRole.addToPolicy(logLambdaPolicy);
    BenchmarkLambdaRole.addToPolicy(enableKeyAccessPolicy);


    // init needed keys
    const sanitizedLang = language.replace("#", "sharp");
    const archType = architecture === 'x86' ? lambda.Architecture.X86_64 : lambda.Architecture.ARM_64;

    for (const operation of operations) {
      for (const memorySize of memorySizes) {
        // Generate the function key
        const functionKey = `${architecture}-${sanitizedLang}-${operation}-${memorySize}`;

        // Determine the handler and code location based on language
        const { handler, fileCodeLocation } = this.getHandlerAndLocation(language, architecture, operation);

        // Create the Lambda function
        const lambdaFunction = new lambda.Function(this, `BKLambda-${functionKey}`, {
          functionName: functionKey,
          runtime: this.getRuntime(language),
          code: lambda.Code.fromAsset(path.resolve(__dirname, fileCodeLocation)),
          handler,
          role: BenchmarkLambdaRole,
          memorySize,
          architecture: archType,
          environment: kmsKeyEnvs[operation],
          // ten minutes
          timeout: cdk.Duration.seconds(600)
        });
        createdChildLambdas[functionKey] = lambdaFunction;
      }
    }

    // generate new lambda urls
    new BKLambdaURLStack(this, `BK-UrlStack-${language}-${architecture}`, {
      BenchmarkLambdas: createdChildLambdas,
      //exitingIamUser: existingAWSUserAcc,
      language: language,
      architecture: architecture
    })

  }
  private getHandlerAndLocation(language: string, architecture: string, operation: string): { handler: string; fileCodeLocation: string } {
    let handler: string;
    let fileCodeLocation: string;

    switch (language) {
      case 'c#':
        handler = `${operation}::LambdaApiProxy.Function::FunctionHandler`;
        fileCodeLocation = `../lambdas/c#/${architecture}/${operation}/${operation}.zip`;
        break;
      case 'go':
        handler = `bootstrap`;
        fileCodeLocation = `../lambdas/go/${architecture}/${operation}/${operation}.zip`;
        break;
      case 'java':
        handler = `com.webb.LambdaHandler::handleRequest`;
        fileCodeLocation = `../lambdas/java/${architecture}/${operation}/${operation}-1.0-SNAPSHOT.jar`;
        break;
      case 'python':
        handler = `${operation}.lambda_handler`;
        fileCodeLocation = `../lambdas/python/${architecture}/${operation}/${operation}.zip`;
        break;
      case 'rust':
        handler = `bootstrap`;
        fileCodeLocation = `../lambdas/rust/${architecture}/${operation}/bootstrap.zip`;
        break;
      case 'typescript':
        handler = `${operation}.handler`;
        fileCodeLocation = `../lambdas/typescript/${architecture}/${operation}/${operation}.zip`;
        break;
      default:
        throw new Error(`No handler and/or code file found for language, operation: ${language}, ${operation}`);
    }

    return { handler, fileCodeLocation };
  }

  private getRuntime(language: string): lambda.Runtime {
    switch (language) {
      case 'python': return lambda.Runtime.PYTHON_3_11;
      case 'typescript': return lambda.Runtime.NODEJS_20_X;
      case 'go': return lambda.Runtime.PROVIDED_AL2023; // Custom Runtime for GO
      case 'java': return lambda.Runtime.JAVA_21;
      case 'c#': return lambda.Runtime.DOTNET_8;
      case 'rust': return lambda.Runtime.PROVIDED_AL2023; // Custom runtime for Rust
      default: throw new Error(`Unsupported language: ${language}`);
    }
  }
}
