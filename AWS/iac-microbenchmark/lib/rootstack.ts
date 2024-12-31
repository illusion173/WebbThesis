
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import { BKIAMStack } from "../lib/iam";
import { BKLambdaStackMain } from "../lib/lambda-main"
import { BKAPIGWStackMain } from "../lib/apigw-main"
interface RootStackProps extends cdk.StackProps {
  languages: string[],
  architectures: string[],
  operations: string[],
  memorySizes: number[],
  kmsKeyEnvs: { [key: string]: { [key: string]: string } },
  kmsKeyArns: { [key: string]: string },
}

// This constitutes as the root stack for the entire deployment of cdk resources.
export class BKRootStack extends cdk.Stack {

  public iamStack: BKIAMStack;
  public mainlambdaStack: BKLambdaStackMain;

  constructor(scope: Construct, id: string, props: RootStackProps) {
    super(scope, id, props);

    const { languages, architectures, operations, memorySizes, kmsKeyEnvs, kmsKeyArns } = props;


    const kmsKeyARNList = Object.values(kmsKeyArns);

    // Iam stack to generate needed IAM role/policy for lambdas.
    this.iamStack = new BKIAMStack(this, "BK-IAMStack", {
      kmsKeyArns: kmsKeyARNList,
    });


    // Created benchmark role
    const lambdaBenchmarkRole = this.iamStack.BenchmarkLambdaRole;

    // Main Lambda Stack where we can expect to obtain all the lambdas from.
    this.mainlambdaStack = new BKLambdaStackMain(this, "Bk-LambdaMainStack", {
      BenchmarkLambdaRole: lambdaBenchmarkRole,
      languages: languages,
      architectures: architectures,
      operations: operations,
      memorySizes: memorySizes,
      kmsKeyEnvs: kmsKeyEnvs,
    });


    // Ensure lambda stack does not build until iam stack does.
    this.mainlambdaStack.addDependency(this.iamStack)

    let lambdaFunctionsMap: {
      [key: string]: { [key: string]: { [key: string]: lambda.Function } }
    } = this.mainlambdaStack.BenchmarkLambdas;

    // Now that we have all our lambdas, lets create APIs.














  }
}

