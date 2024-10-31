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
struct EncryptedMessageStruct {
    ciphertext: String,
    iv: String,
    tag: String,
    encrypted_key: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Get the KMS key ARN from environment variables
    let aes_kms_key_id = env::var("AES_KMS_KEY_ARN").map_err(|_| "KMS key ARN not set")?;

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

    // Attempt to encrypt the message using KMS
    match kms_encrypt_message(&kms_client, &aes_kms_key_id, message_blob).await {
        Ok(encrypted_message_struct) => {
            // Serialize the struct to a JSON string
            let str_encrypted_message_struct = serde_json::to_string(&encrypted_message_struct)?;
            println!("{}", str_encrypted_message_struct);
            Ok(())
        }
        Err(e) => Err(format!("Error encrypting message: {}", e).into()),
    }
}

/// Function to encrypt a message using AWS KMS. AES 256
async fn kms_encrypt_message(
    kms_client: &kms::Client,
    key_id: &str,
    message: Blob,
) -> Result<EncryptedMessageStruct, Box<dyn Error>> {
    // Generate a data key using KMS
    let data_key_output = kms_client
        .generate_data_key()
        .key_id(key_id)
        .key_spec("AES_256".into())
        .send()
        .await
        .map_err(|err| format!("Failed to generate data key: {}", err))?;

    let plaintext_data_key = data_key_output
        .plaintext
        .ok_or_else(|| "No plaintext data key returned")?;

    let plaintext_dk_u8 = plaintext_data_key.into_inner(); // Convert

    let encrypted_data_key = data_key_output
        .ciphertext_blob
        .ok_or_else(|| "No encrypted data key returned")?;

    // Generate IV and tag for AES-GCM
    let mut iv = [0u8; 16]; // Initialize a 16-byte array for IV
    openssl::rand::rand_bytes(&mut iv).map_err(|_| "Failed to generate IV")?;

    // AES-GCM encryption using OpenSSL
    let cipher = openssl::symm::Cipher::aes_256_gcm();
    let mut tag = vec![0; 16]; // 16-byte tag for AES-GCM

    let ciphertext = openssl::symm::encrypt_aead(
        cipher,
        &plaintext_dk_u8,
        Some(&iv),        // Use the IV we generated
        &[],              // No additional authenticated data (AAD)
        message.as_ref(), // The message to encrypt
        &mut tag,         // Output tag buffer
    )
    .map_err(|_| "AES Encryption failed")?;

    // Create the encrypted message struct, with Base64-encoded values
    let encrypted_message_struct = EncryptedMessageStruct {
        ciphertext: encode(&ciphertext),
        iv: encode(&iv),
        tag: encode(&tag),
        encrypted_key: encode(&encrypted_data_key),
    };

    Ok(encrypted_message_struct)
}
