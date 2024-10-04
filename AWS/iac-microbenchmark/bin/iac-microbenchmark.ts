#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { IacMicrobenchmark } from '../lib/iac-microbenchmark';

const app = new cdk.App();
new IacMicrobenchmark(app, 'IACMKStack');
