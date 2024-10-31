use aws_sdk_kms::{self as kms, primitives::Blob, Client};
use base64::{decode, encode};
use serde::{Deserialize, Serialize};
use std::env;
use std::error::Error;

#[derive(Serialize, Deserialize, Debug)]
struct ECC256Request {
    message: String,
    signature: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct ECC256Response {
    valid: bool,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Get the KMS key ARN from environment variables
    let ecc_kms_key_id =
        env::var("ECC256_KMS_KEY_ARN").map_err(|_| "ECC 256 KMS key ARN not set?")?;

    // Get JSON input from command line
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        return Err("Usage: ./rustexecutable '{\"message\":\"your_message_here\", \"signature\":\"your_signature_here\"}'".into());
    }

    let body_str = &args[1];

    // Parse the input JSON
    let message_struct: ECC256Request = serde_json::from_str(body_str)
        .map_err(|_| "Invalid Request Body, missing message or signature.")?;

    // Initialize the KMS client
    let kms_client = kms::Client::new(&aws_config::load_from_env().await);

    let message = message_struct.message;
    let signature = message_struct.signature;

    // Attempt to verify the message using KMS
    match kms_client_verify_message(&kms_client, &ecc_kms_key_id, &message, &signature).await {
        Ok(verify_response) => {
            // Serialize the verification response to a JSON string
            let str_verify_response = serde_json::to_string(&verify_response)?;
            println!("{}", str_verify_response);
            Ok(())
        }
        Err(e) => Err(format!("Error verifying message: {}", e).into()),
    }
}

async fn kms_client_verify_message(
    kms_client: &Client,
    key_id: &str,
    message: &str,
    signature_b64: &str,
) -> Result<ECC256Response, Box<dyn Error>> {
    // Decode the base64-encoded signature
    let signature = decode(signature_b64).map_err(|_| "Failed to decode signature ECC256")?;

    let signature_blob = Blob::new(signature);
    let message_blob = Blob::new(message.as_bytes());

    // Perform the verification
    let verify_output = kms_client
        .verify()
        .key_id(key_id)
        .message(message_blob)
        .message_type(aws_sdk_kms::types::MessageType::Raw)
        .signature(signature_blob)
        .signing_algorithm(aws_sdk_kms::types::SigningAlgorithmSpec::EcdsaSha256)
        .send()
        .await?;

    let is_valid = verify_output.signature_valid;

    let verify_response = ECC256Response { valid: is_valid };

    Ok(verify_response)
}
