#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { IaCIam } from "../lib/iam";
import { IaCAPIGw } from "../lib/api_gw";
import { IaCLambdas } from "../lib/lambdas"
import { IaCExports } from "../lib/iac-exports"

// USE THIS TYPESCRIPT FILE TO MANAGE LAMBDAS AND KMS ARNS
import { languages, architectures, operations, memory_sizes, kmsKeyArns, operationKeyEnvs } from "./iac-inputs"

// Assign a random id int for tracking in AWS console.
const iacId = Math.floor(Math.random() * 9999) + 1;

// Extract the needed keys here
const kmsKeyARNList = Object.values(kmsKeyArns);

const app = new cdk.App();

const IamStack = new IaCIam(app, 'IaCMKStack' + iacId, {
  iacId: iacId,
  kmsKeyArns: kmsKeyARNList,
});

// Create Lambdas here
const LambdaStack = new IaCLambdas(app, 'IaCMKStack' + iacId, {
  iacId: iacId,
  programmingLanguages: languages,
  architectures: architectures,
  operations: operations,
  memorySizes: memory_sizes,
  benchmarkLambdaRole: IamStack.BenchmarkLambdaRole,
  operationKeyEnvs: operationKeyEnvs

});

// Create API here that will interact with the Lambdas
const APIGWStack = new IaCAPIGw(app, 'IaCMKStack' + iacId, {
  iacId: iacId,
});

new IaCExports(app, 'IaCMKStack' + iacId);

