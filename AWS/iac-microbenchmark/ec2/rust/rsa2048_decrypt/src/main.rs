use aws_sdk_kms::{self as kms, primitives::Blob, Client};
use base64::decode;
use serde::{Deserialize, Serialize};
use std::env;
use std::error::Error;

#[derive(Serialize, Deserialize, Debug)]
struct RSA2048DecryptRequest {
    ciphertext: String,
    iv: String,
    encrypted_key: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct RSA2048DecryptResponse {
    message: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Get the KMS key ARN from environment variables
    let rsa_kms_key_id =
        env::var("RSA2048_KMS_KEY_ARN").map_err(|_| "RSA 2048 KMS key ARN not set?")?;

    // Get JSON input from command line
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        return Err("Usage: ./rustexecutable '{\"ciphertext\":\"your_ciphertext_here\", \"iv\":\"your_iv_here\", \"encrypted_key\":\"your_encrypted_key_here\"}'".into());
    }

    let body_str = &args[1];

    // Parse the input JSON
    let request_struct: RSA2048DecryptRequest =
        serde_json::from_str(body_str).map_err(|_| "Invalid Request Body, missing data.")?;

    // Initialize the KMS client
    let kms_client = kms::Client::new(&aws_config::load_from_env().await);

    // Attempt to decrypt the message using KMS
    match aws_kms_rsa_decrypt(&kms_client, &rsa_kms_key_id, &request_struct).await {
        Ok(decrypted_message) => {
            // Print the decrypted message
            println!("{}", decrypted_message);
            Ok(())
        }
        Err(e) => Err(format!("Error decrypting message: {}", e).into()),
    }
}

async fn aws_kms_rsa_decrypt(
    kms_client: &Client,
    key_id: &str,
    request: &RSA2048DecryptRequest,
) -> Result<String, Box<dyn Error>> {
    // Step 1: Decode the base64-encoded AES key, IV, and ciphertext
    let encrypted_aes_key = decode(&request.encrypted_key)
        .map_err(|e| format!("Failed to decode encrypted_key: {}", e))?;

    let iv = decode(&request.iv).map_err(|e| format!("Failed to decode IV: {}", e))?;

    let ciphertext =
        decode(&request.ciphertext).map_err(|e| format!("Failed to decode ciphertext: {}", e))?;

    // Step 2: Decrypt the AES key using AWS KMS
    let response = kms_client
        .decrypt()
        .key_id(key_id)
        .ciphertext_blob(Blob::new(encrypted_aes_key)) // Decrypt the AES key
        .encryption_algorithm(kms::types::EncryptionAlgorithmSpec::RsaesOaepSha256)
        .send()
        .await
        .map_err(|err| format!("KMS decryption failed: {}", err))?;

    let decrypted_aes_key = response
        .plaintext()
        .expect("No Plaintext in KMS response")
        .as_ref()
        .to_vec();

    // Step 3: Decrypt the message using AES-256-CTR with OpenSSL
    let cipher = openssl::symm::Cipher::aes_256_ctr();
    let mut crypter = openssl::symm::Crypter::new(
        cipher,
        openssl::symm::Mode::Decrypt,
        &decrypted_aes_key,
        Some(&iv),
    )
    .map_err(|e| format!("Failed to create Crypter: {}", e))?;

    let mut decrypted_message = vec![0; ciphertext.len() + cipher.block_size()];
    crypter
        .update(&ciphertext, &mut decrypted_message)
        .map_err(|e| format!("Failed to decrypt ciphertext: {}", e))?;

    let count = crypter
        .finalize(&mut decrypted_message)
        .map_err(|e| format!("Failed to finalize decryption: {}", e))?;

    decrypted_message.truncate(count);

    // Convert decrypted message to string
    let decrypted_message_str = String::from_utf8(decrypted_message)
        .map_err(|e| format!("Failed to convert decrypted message to string: {}", e))?;

    Ok(decrypted_message_str)
}
