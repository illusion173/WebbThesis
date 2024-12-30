import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import path from 'path';

interface ChildStackLambdasProps extends cdk.StackProps {
  iacId: number
  BenchmarkLambdaRole: iam.Role,
  language: string,
  architectures: string[],
  operations: string[],
  memorySizes: number[],
  kmsKeyEnvs: { [key: string]: { [key: string]: string } },
}

export class ChildStackLambdas extends cdk.Stack {

  public readonly createdChildLambdas: { [key: string]: { [key: string]: lambda.Function } };

  constructor(scope: Construct, id: string, props: ChildStackLambdasProps) {

    super(scope, id, props);
    this.createdChildLambdas = {};

    const { iacId, BenchmarkLambdaRole, language, architectures, operations, memorySizes, kmsKeyEnvs } = props;

    // annoying, in here it'll be csharp as the key lookup, but in the physical name itll be csharp
    const sanitizedLang = language.replace("#", "sharp");
    this.createdChildLambdas[language] = {};

    for (const architecture of architectures) {
      const archType = architecture === 'x86' ? lambda.Architecture.X86_64 : lambda.Architecture.ARM_64;

      for (const operation of operations) {
        for (const memorySize of memorySizes) {
          // Generate the function key
          const functionKey = `${architecture}-${sanitizedLang}-${operation}-${memorySize}`;

          // Determine the handler and code location based on language
          const { handler, fileCodeLocation } = this.getHandlerAndLocation(language, architecture, operation);

          // Create the Lambda function
          const lambdaFunction = new lambda.Function(this, `Lambda-${functionKey}-${iacId}`, {
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

          // Store the function in the dictionary
          this.createdChildLambdas[language][functionKey] = lambdaFunction;
        }
      }
    }
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
