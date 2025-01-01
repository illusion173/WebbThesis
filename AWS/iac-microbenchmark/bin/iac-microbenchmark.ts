#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { BKLambdaBuildStack } from "../lib/lambda-build"

// USE THE TYPESCRIPT FILE iac-inputs.ts TO MANAGE POTENTIAL LAMBDAS AND KMS ARNS
import { languages, architectures, operations, memory_sizes, kmsKeyArns, operationKeyEnvs } from "./iac-inputs"

const app = new cdk.App();

const kmsKeyARNList = Object.values(kmsKeyArns);


// To avoid creating too many stacks we will use a pattern like this to avoid hitting limits by AWS.
// functionkey will be
// sanitizedLang is c# -> csharp
// KEEP NOTE the [language] above will be c#
//const functionKey = `${architecture}-${sanitizedLang}-${operation}-${memorySize}`;
// LIKE THIS
/*
*/
// So we will create a stack per language and architecture.
//
for (const architecture of architectures) {

  for (const language of languages) {
    // specific
    let sanitizedLang = language.replace("#", "sharp")

    const newLambdaBuildStack = new BKLambdaBuildStack(app, `IaCBenchMark-Build-Lambdas-${sanitizedLang}-${architecture}`, {

      //BenchmarkLambdaRole: iamStack.BenchmarkLambdaRole,
      language: language,
      architecture: architecture,
      operations: operations,
      memorySizes: memory_sizes,
      kmsKeyEnvs: operationKeyEnvs,
      //existingAWSUser: iamStack.existingAWSUserAcc
      kmsKeyARNList: kmsKeyARNList
    });

  }
}








