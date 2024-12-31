import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

interface APIGWDeploymentStackAPIGWProps extends cdk.StackProps {
  readonly restApiId: string,
  readonly benchmarkMethods: apigateway.Method[],
  iacId: string,
  architecture: string,
  language: string,
}

export class DeployStack extends cdk.Stack {

  constructor(scope: Construct, id: string, props: APIGWDeploymentStackAPIGWProps) {

    super(scope, id, props);

    const { restApiId, benchmarkMethods, iacId, architecture, language } = props;

    const deployment = new apigateway.Deployment(this, `APIGWDeploymentFor-${architecture}-${language}-${iacId}`, {
      api: apigateway.RestApi.fromRestApiId(this, `IacBenchmark-API-${architecture}-${language}-${iacId}`, restApiId),
    })

    for (const method of benchmarkMethods) {
      deployment.node.addDependency(method);
    }

    //const newStage= new apigateway.Stage(this, `prodStage-${architecture}-${language}-${iacId}`, { deployment: deployment })
  }

}
