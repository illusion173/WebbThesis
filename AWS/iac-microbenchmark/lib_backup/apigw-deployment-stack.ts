import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

interface APIGWDeploymentStackAPIGWProps extends cdk.StackProps {
  readonly restApiId: string,
  readonly benchmarkMethods: apigateway.Method[],
  iacId: number
}

export class DeployStack extends cdk.Stack {

  constructor(scope: Construct, id: string, props: APIGWDeploymentStackAPIGWProps) {

    super(scope, id, props);

    const { restApiId, benchmarkMethods, iacId } = props;

    const deployment = new apigateway.Deployment(this, 'APIGWDeployment', {
      api: apigateway.RestApi.fromRestApiId(this, `IacBenchmark-API-${iacId}`, restApiId),
    })

    /*
    for (const method in benchmarkMethods) {
      deployment.node.addDependency(method)
    }
    */
    /*new apigateway.Stage(this, 'ProdStage', { deployment: deployment })*/
  }
}
