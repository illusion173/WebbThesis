import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { BKLambdaChildStack } from "./lambda-child"
interface MainStackLambdasProps extends cdk.NestedStackProps {
  BenchmarkLambdaRole: iam.Role,
  languages: string[],
  architectures: string[],
  operations: string[],
  memorySizes: number[],
  kmsKeyEnvs: { [key: string]: { [key: string]: string } },
}

export class BKLambdaStackMain extends cdk.NestedStack {

  public lambdaChildrenStacks: BKLambdaChildStack[];

  public readonly BenchmarkLambdas: {
    [key: string]: { [key: string]: { [key: string]: lambda.Function } }
  };

  constructor(scope: Construct, id: string, props: MainStackLambdasProps) {

    super(scope, id, props);

    const { BenchmarkLambdaRole, languages, architectures, operations, memorySizes, kmsKeyEnvs } = props;
    this.lambdaChildrenStacks = []


    // To avoid creating too many stacks we will use a pattern like this to avoid hitting limits by AWS.
    // createdBenchmarkLambdas[language][architecture][functionkey] = lambdafunction
    // functionkey will be
    // sanitizedLang is c# -> csharp
    // KEEP NOTE the [language] above will be c# 
    //const functionKey = `${architecture}-${sanitizedLang}-${operation}-${memorySize}`;
    let createdBenchmarkLambdas: {
      [key: string]: { [key: string]: { [key: string]: lambda.Function } }
    } = {};

    // So we will create a child stack per language.
    for (const language of languages) {

      const childStack = new BKLambdaChildStack(this, `IaCBenchMark-Child-Lambdas-${language}`, {
        BenchmarkLambdaRole: BenchmarkLambdaRole,
        language: language,
        architectures: architectures,
        operations: operations,
        memorySizes: memorySizes,
        kmsKeyEnvs: kmsKeyEnvs,
      });

      // Collect children
      this.lambdaChildrenStacks.push(childStack);

      // Grab new Lambda functions
      const createdLambdasFromChild = childStack.createdChildLambdas;

      // Merge on top level, languages combined here
      createdBenchmarkLambdas = { ...createdBenchmarkLambdas, ...createdLambdasFromChild };
    }
    this.BenchmarkLambdas = createdBenchmarkLambdas;

  }
}
