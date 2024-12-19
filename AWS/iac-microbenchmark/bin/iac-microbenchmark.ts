#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { IaCIam } from "../lib/iam";
import { IaCAPIGw } from "../lib/api_gw";
import { IaCLambdas } from "../lib/lambdas"
import { IaCExports } from "../lib/iac-exports"

const app = new cdk.App();

new IaCIam(app, 'IaCMKStack');
new IaCAPIGw(app, 'IaCMKStack');
new IaCLambdas(app, 'IaCMKStack');
new IaCExports(app, 'IaCMKStack');
