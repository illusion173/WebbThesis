
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { ChildStackLambdas } from "./lambda-child-stack"

interface MainStackLambdasProps extends cdk.StackProps {
  iacId: number
  BenchmarkLambdaRole: iam.Role,
  languages: string[],
  architectures: string[],
  operations: string[],
  memorySizes: number[],
  kmsKeyEnvs: { [key: string]: { [key: string]: string } },
}

export class IacMainStackLambdas extends cdk.Stack {
  public readonly BenchmarkLambdas: {
    [key: string]: { [key: string]: { [key: string]: lambda.Function } }
  };

  constructor(scope: Construct, id: string, props: MainStackLambdasProps) {

    super(scope, id, props);

    const { iacId, BenchmarkLambdaRole, languages, architectures, operations, memorySizes, kmsKeyEnvs } = props;
    // Categorize by language and architecture, then inside the itll be {lambdakey, lambdafunction}
    // lambda key will be then something like python/arm for lookup
    // where sanitizedLang will be c# -> csharp
    let createdBenchmarkLambdas: {
      [key: string]: { [key: string]: { [key: string]: lambda.Function } }
    } = {};

    // So we will create a child stack per language.
    for (const language of languages) {

      const childStack = new ChildStackLambdas(this, `IaCBenchMark-Child-Lambdas-${language}-${iacId}`, {
        iacId: iacId,
        BenchmarkLambdaRole: BenchmarkLambdaRole,
        language: language,
        architectures: architectures,
        operations: operations,
        memorySizes: memorySizes,
        kmsKeyEnvs: kmsKeyEnvs,
      });

      // Grab new Lambda functions
      const createdLambdasFromChild = childStack.createdChildLambdas;

      // Merge on top level, languages combined here
      createdBenchmarkLambdas = { ...createdBenchmarkLambdas, ...createdLambdasFromChild };
    }
    this.BenchmarkLambdas = createdBenchmarkLambdas;

  }
}
