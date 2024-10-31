use aws_sdk_kms::{self as kms, primitives::Blob};
use base64::encode;
use serde::{Deserialize, Serialize};
use std::env;
use std::error::Error;

#[derive(Serialize, Deserialize, Debug)]
struct MessageStruct {
    message: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct SignatureStruct {
    signature: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Get the KMS key ARN from environment variables
    let sha_kms_key_id = env::var("SHA256_KMS_KEY_ARN").map_err(|_| "KMS key ARN not set")?;

    // Get JSON input from command line
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        return Err("Usage: ./rustexecutable '{\"message\":\"your_message_here\"}'".into());
    }

    let body_str = &args[1];

    // Parse the input JSON
    let message_struct: MessageStruct = serde_json::from_str(body_str)
        .map_err(|_| "Invalid Request Body, missing message or incorrect format.")?;

    // Convert the message to bytes
    let message_blob = Blob::new(message_struct.message.as_bytes());

    // Initialize the KMS client
    let config = aws_config::load_from_env().await;
    let kms_client = kms::Client::new(&config);

    // Attempt to sign the message using KMS
    match kms_sign_message(&kms_client, &sha_kms_key_id, message_blob).await {
        Ok(signature) => {
            let sig_struct = SignatureStruct { signature };

            // Serialize the struct to a JSON string
            let str_sig_struct = serde_json::to_string(&sig_struct)?;
            println!("{}", str_sig_struct);

            Ok(())
        }
        Err(e) => Err(format!("Error signing message: {}", e).into()),
    }
}

/// Function to sign a message using AWS KMS.
async fn kms_sign_message(
    kms_client: &kms::Client,
    key_id: &str,
    message: Blob,
) -> Result<String, Box<dyn Error>> {
    let mac_output = kms_client
        .generate_mac()
        .key_id(key_id)
        .message(message)
        .mac_algorithm(aws_sdk_kms::types::MacAlgorithmSpec::HmacSha256)
        .send()
        .await
        .map_err(|err| format!("Failed to generate mac hash: {}", err))?;

    let mac = mac_output.mac.ok_or_else(|| "No Mac hash returned")?;

    Ok(encode(mac.as_ref()))
}
