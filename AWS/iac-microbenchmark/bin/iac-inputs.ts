// This is where one can determine the exact test cases one want's to create.
export const architectures: string[] = [
  "x86",
  "arm"
]

export const languages: string[] = [
  'c#',
  'go',
  'java',
  'python',
  'rust',
  'typescript',
]

export const operations: string[] = [
  'aes256_decrypt',
  'aes256_encrypt',
  'ecc256_sign',
  'ecc256_verify',
  'ecc384_sign',
  'ecc384_verify',
  'rsa2048_decrypt',
  'rsa2048_encrypt',
  'rsa3072_decrypt',
  'rsa3072_encrypt',
  'rsa4096_decrypt',
  'rsa4096_encrypt',
  'sha256',
  'sha384',
]

// All in MB
export const memory_sizes: number[] = [
  128,
  256,
  512,
  1024,
  1536,
  2048
]
// Kind of gross, but will work for referencing kms key arns based on operation
// Used to set the env vars for the lambda functions.
export const operationKeyEnvs: { [key: string]: { [key: string]: string } } = {
  'aes256_decrypt': { 'AES_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/d8af2caf-3762-4151-a168-d0848b700a2c' },
  'aes256_encrypt': { 'AES_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/d8af2caf-3762-4151-a168-d0848b700a2c' },
  'ecc256_sign': { 'ECC256_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/a0bb4951-0a8c-47ed-901d-cd1658305239' },
  'ecc256_verify': { 'ECC256_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/a0bb4951-0a8c-47ed-901d-cd1658305239' },
  'ecc384_sign': { 'ECC384_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/7d27cfe2-5863-4f7c-8257-a452e582ee1a' },
  'ecc384_verify': { 'ECC384_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/7d27cfe2-5863-4f7c-8257-a452e582ee1a' },
  'rsa2048_decrypt': { 'RSA2048_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/d644cd8f-4983-4aca-a79b-8be0e9e1f610' },
  'rsa2048_encrypt': { 'RSA2048_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/d644cd8f-4983-4aca-a79b-8be0e9e1f610' },
  'rsa3072_decrypt': { 'RSA3072_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/e42b73f3-1996-4495-8634-18ef607feac7' },
  'rsa3072_encrypt': { 'RSA3072_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/e42b73f3-1996-4495-8634-18ef607feac7' },
  'rsa4096_decrypt': { 'RSA4096_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/2ed02f0d-6420-4a55-8378-820e2b5e228c' },
  'rsa4096_encrypt': { 'RSA4096_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/2ed02f0d-6420-4a55-8378-820e2b5e228c' },
  'sha256': { 'SHA256_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/4a177bdb-5d10-4043-a67b-12b7036f3ada' },
  'sha384': { 'SHA384_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/fe351b9f-2b6d-4473-bebe-f50ad4ca2d42' },

}

// For reference.
export const kmsKeyArns: { [key: string]: string } = {
  'SHA256_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/4a177bdb-5d10-4043-a67b-12b7036f3ada',
  'SHA384_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/fe351b9f-2b6d-4473-bebe-f50ad4ca2d42',
  'AES_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/d8af2caf-3762-4151-a168-d0848b700a2c',
  'RSA2048_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/d644cd8f-4983-4aca-a79b-8be0e9e1f610',
  'RSA3072_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/e42b73f3-1996-4495-8634-18ef607feac7',
  'RSA4096_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/2ed02f0d-6420-4a55-8378-820e2b5e228c',
  'ECC256_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/a0bb4951-0a8c-47ed-901d-cd1658305239',
  'ECC384_KMS_KEY_ARN': 'arn:aws:kms:us-east-1:417838760454:key/7d27cfe2-5863-4f7c-8257-a452e582ee1a'
}

