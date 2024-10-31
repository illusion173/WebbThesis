use aws_sdk_kms::{self as kms, primitives::Blob};
use base64::{decode, encode};
use serde::{Deserialize, Serialize};
use std::env;
use std::error::Error;

#[derive(Serialize, Deserialize, Debug)]
struct EncryptedMessageStruct {
    ciphertext: String,
    iv: String,
    tag: String,
    encrypted_key: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct MessageStruct {
    message: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Get the KMS key ARN from environment variables
    let aes_kms_key_id = env::var("AES_KMS_KEY_ARN").map_err(|_| "KMS key ARN not set")?;

    // Get JSON input from command line
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        return Err("Usage: ./rustexecutable '{\"ciphertext\":\"your_ciphertext_here\", \"iv\":\"your_iv_here\", \"tag\":\"your_tag_here\", \"encrypted_key\":\"your_encrypted_key_here\"}'".into());
    }

    let body_str = &args[1];

    // Parse the input JSON
    let encrypted_message_struct: EncryptedMessageStruct = serde_json::from_str(body_str)
        .map_err(|_| "Invalid Request Body, missing EncryptedMessageStruct props")?;

    // Initialize the KMS client
    let config = aws_config::load_from_env().await;
    let kms_client = kms::Client::new(&config);

    // Attempt to decrypt the message using KMS
    match kms_decrypt_message(&kms_client, &aes_kms_key_id, encrypted_message_struct).await {
        Ok(decrypted_message_struct) => {
            // Serialize the struct to a JSON string
            let str_decrypted_message_struct = serde_json::to_string(&decrypted_message_struct)?;
            println!("{}", str_decrypted_message_struct);
            Ok(())
        }
        Err(e) => Err(format!("Error decrypting message: {}", e).into()),
    }
}

/// Function to decrypt a message using AWS KMS. AES 256
async fn kms_decrypt_message(
    kms_client: &kms::Client,
    key_id: &str,
    encrypted_message: EncryptedMessageStruct,
) -> Result<MessageStruct, Box<dyn Error>> {
    // Decrypt the data key using KMS
    let encryption_key_decoded = decode(&encrypted_message.encrypted_key)
        .map(Blob::new)
        .map_err(|_| "Failed to decode encrypted key")?;

    let data_key_output = kms_client
        .decrypt()
        .key_id(key_id)
        .ciphertext_blob(encryption_key_decoded)
        .send()
        .await
        .map_err(|err| format!("Failed to decrypt data key: {}", err))?;

    let plaintext_data_key = data_key_output
        .plaintext
        .ok_or_else(|| "No plaintext data key returned")?;

    let plaintext_dk_u8 = plaintext_data_key.into_inner();

    // Decode the IV, tag, and ciphertext
    let iv = decode(&encrypted_message.iv).map_err(|_| "Failed to decode IV")?;
    let tag = decode(&encrypted_message.tag).map_err(|_| "Failed to decode tag")?;
    let ciphertext =
        decode(&encrypted_message.ciphertext).map_err(|_| "Failed to decode ciphertext")?;

    // AES-GCM decryption
    let cipher = openssl::symm::Cipher::aes_256_gcm();

    let decrypted_message =
        openssl::symm::decrypt_aead(cipher, &plaintext_dk_u8, Some(&iv), &[], &ciphertext, &tag)
            .map_err(|_| "AES Decryption failed")?;

    let decrypted_message_struct = MessageStruct {
        message: String::from_utf8(decrypted_message).map_err(|_| "Invalid UTF-8")?,
    };

    Ok(decrypted_message_struct)
}
