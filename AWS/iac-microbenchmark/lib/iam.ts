import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';

interface IAMStackProps extends cdk.StackProps {
  kmsKeyArns: string[],
  iacId: number
}

export class IaCIam extends cdk.Stack {
  public readonly BenchmarkLambdaRole: iam.Role;

  constructor(scope: Construct, id: string, props: IAMStackProps) {
    super(scope, id, props);

    const { kmsKeyArns, iacId } = props;

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
      ],
      resources: kmsKeyArns
    });

    const lambdaRoleName: string = "benchmarkLambdaRole-" + iacId;

    const BenchmarkLambdaRole = new iam.Role(this, lambdaRoleName, {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    BenchmarkLambdaRole.addToPolicy(logLambdaPolicy);
    BenchmarkLambdaRole.addToPolicy(enableKeyAccessPolicy);

    this.BenchmarkLambdaRole = BenchmarkLambdaRole;

  }
}

