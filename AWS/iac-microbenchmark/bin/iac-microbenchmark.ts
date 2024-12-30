#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { IaCIam } from "../lib/iam";
import { IacMainStackLambdas } from "../lib/lambda-main-stack"
import { IacMainStackAPIGw } from "../lib/apigw-main-stack"

// USE THE TYPESCRIPT FILE iac-inputs.ts TO MANAGE POTENTIAL LAMBDAS AND KMS ARNS
import { languages, architectures, operations, memory_sizes, kmsKeyArns, operationKeyEnvs } from "./iac-inputs"

// Assign a random id int for tracking in AWS console.
const iacId = Math.floor(Math.random() * 9999) + 1;

// Extract the needed keys here
const kmsKeyARNList = Object.values(kmsKeyArns);

const app = new cdk.App();

const IamStack = new IaCIam(app, 'IaCBenchMark-IAM-' + iacId, {
  iacId: iacId,
  kmsKeyArns: kmsKeyARNList,
});

// Grab role for lambdas.
const lambdaBenchmarkRole = IamStack.BenchmarkLambdaRole;

const lambdaFunctionsStack = new IacMainStackLambdas(app, 'IaCBenchMark-Parent-Lambdas-' + iacId, {
  iacId: iacId,
  BenchmarkLambdaRole: lambdaBenchmarkRole,
  languages: languages,
  architectures: architectures,
  operations: operations,
  memorySizes: memory_sizes,
  kmsKeyEnvs: operationKeyEnvs,
});

const lambdaFunctions = lambdaFunctionsStack.BenchmarkLambdas;

new IacMainStackAPIGw(app, "IaCBenchmark-Parent-APIGW-" + iacId, {
  iacId: iacId,
  BenchmarkLambdas: lambdaFunctions,
  languages: languages,
  architectures: architectures,
})


