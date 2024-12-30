import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import path from 'path';

interface ChildStackAPIGWProps extends cdk.StackProps {
  iacId: number,
  filteredBenchmarkLambdas: { [key: string]: lambda.Function }
  language: string,
  architectures: string[],
  operations: string[],
  memorySizes: number[],
  baseAPIUrl: string,
}

export class ChildStackAPIGW extends cdk.Stack {

  public readonly createdAPIGWUrls: { [key: string]: string };

  constructor(scope: Construct, id: string, props: ChildStackAPIGWProps) {

    super(scope, id, props);
    this.createdAPIGWUrls = {};
    const { iacId, filteredBenchmarkLambdas, language, architectures, operations, memorySizes } = props;



  }
}
