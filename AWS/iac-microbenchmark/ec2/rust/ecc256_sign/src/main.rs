use aws_sdk_kms::{self as kms, primitives::Blob, Client};
use base64::encode;
use serde::{Deserialize, Serialize};
use std::env;
use std::error::Error;

#[derive(Serialize, Deserialize, Debug)]
struct ECC256Request {
    message: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct ECC256Response {
    signature: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Get the KMS key ARN from environment variables
    let ecc_kms_key_id =
        env::var("ECC256_KMS_KEY_ARN").map_err(|_| "ECC 256 KMS key ARN not set?")?;

    // Get JSON input from command line
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        return Err("Usage: ./rustexecutable '{\"message\":\"your_message_here\"}'".into());
    }

    let body_str = &args[1];

    // Parse the input JSON
    let message_struct: ECC256Request = serde_json::from_str(body_str)
        .map_err(|_| "Invalid Request Body, missing message or incorrect format.")?;

    // Initialize the KMS client
    let kms_client = kms::Client::new(&aws_config::load_from_env().await);

    let message = message_struct.message;

    // Attempt to sign the message using KMS
    match kms_client_sign_message(&kms_client, &ecc_kms_key_id, &message).await {
        Ok(signature_struct) => {
            // Serialize the signature response to a JSON string
            let str_signature_struct = serde_json::to_string(&signature_struct)?;
            println!("{}", str_signature_struct);
            Ok(())
        }
        Err(e) => Err(format!("Error signing message: {}", e).into()),
    }
}

async fn kms_client_sign_message(
    kms_client: &Client,
    key_id: &str,
    message: &str,
) -> Result<ECC256Response, Box<dyn Error>> {
    let message_blob = Blob::new(message);
    let sign_output = kms_client
        .sign()
        .key_id(key_id)
        .message(message_blob)
        .message_type(aws_sdk_kms::types::MessageType::Raw)
        .signing_algorithm(aws_sdk_kms::types::SigningAlgorithmSpec::EcdsaSha256)
        .send()
        .await?;

    let signature = sign_output
        .signature()
        .ok_or_else(|| "No Signature returned? ECC256 Sign")?;

    // Encode the signature to base64
    let sig_b64 = encode(signature);

    let signature_response = ECC256Response { signature: sig_b64 };

    Ok(signature_response)
}
