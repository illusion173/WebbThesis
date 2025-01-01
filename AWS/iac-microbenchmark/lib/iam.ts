import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';

interface IAMStackProps extends cdk.StackProps {
  kmsKeyArns: string[],
}

export class BKIAMStack extends cdk.Stack {
  public BenchmarkLambdaRole: iam.Role;
  public existingAWSUserAcc: iam.IUser;

  constructor(scope: Construct, id: string, props: IAMStackProps) {
    super(scope, id, props);

    const { kmsKeyArns } = props;

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

    const lambdaRoleName: string = "BKLambdaRole";

    const BenchmarkLambdaRole = new iam.Role(this, lambdaRoleName, {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    BenchmarkLambdaRole.addToPolicy(logLambdaPolicy);
    BenchmarkLambdaRole.addToPolicy(enableKeyAccessPolicy);

    this.BenchmarkLambdaRole = BenchmarkLambdaRole;

    this.existingAWSUserAcc = iam.User.fromUserName(this, 'ExistingAWSUser', 'illusion173');

  }
}

