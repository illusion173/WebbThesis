use aws_sdk_kms::{self as kms, primitives::Blob, Client};
use base64::decode;
use openssl::symm::{Cipher, Crypter, Mode};
use serde::{Deserialize, Serialize};
use std::env;
use std::error::Error;

#[derive(Serialize, Deserialize, Debug)]
struct RSA3072DecryptRequest {
    ciphertext: String,
    iv: String,
    encrypted_aes_key: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct RSA3072DecryptResponse {
    message: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Get the KMS key ARN from environment variables
    let rsa_kms_key_id =
        env::var("RSA3072_KMS_KEY_ARN").map_err(|_| "RSA 3072 KMS key ARN not set?")?;

    // Get JSON input from command line
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        return Err("Usage: ./rustexecutable '{\"ciphertext\":\"your_ciphertext_here\", \"iv\":\"your_iv_here\", \"encrypted_aes_key\":\"your_encrypted_aes_key_here\"}'".into());
    }

    let body_str = &args[1];

    // Parse the input JSON
    let request_struct: RSA3072DecryptRequest =
        serde_json::from_str(body_str).map_err(|_| "Invalid Request Body, missing data.")?;

    // Initialize the KMS client
    let kms_client = kms::Client::new(&aws_config::load_from_env().await);

    // Attempt to decrypt the message using KMS
    match aws_kms_rsa_decrypt(&kms_client, &rsa_kms_key_id, &request_struct).await {
        Ok(decrypted_message) => {
            // Print the decrypted message
            let response_struct = RSA3072DecryptResponse {
                message: decrypted_message,
            };

            let rsp_str = serde_json::to_string(&response_struct)?;
            println!("{}", rsp_str);
            Ok(())
        }
        Err(e) => Err(format!("Error decrypting message: {}", e).into()),
    }
}

async fn aws_kms_rsa_decrypt(
    kms_client: &Client,
    key_id: &str,
    request: &RSA3072DecryptRequest,
) -> Result<String, Box<dyn Error>> {
    // Step 1: Decode the base64-encoded AES key, IV, and ciphertext
    let encrypted_aes_key = decode(&request.encrypted_aes_key)
        .map_err(|e| format!("Failed to decode encrypted_aes_key: {}", e))?;

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
        .as_ref();

    // Decrypt the data using AES-CTR
    let cipher = Cipher::aes_256_ctr();
    let mut decryptor = Crypter::new(cipher, Mode::Decrypt, decrypted_aes_key, Some(&iv)).unwrap();
    let mut plaintext = vec![0; ciphertext.len() + cipher.block_size()];
    let mut count = decryptor.update(&ciphertext, &mut plaintext).unwrap();
    count += decryptor.finalize(&mut plaintext[count..]).unwrap();

    plaintext.truncate(count);
    // Convert decrypted message to string
    let decrypted_message_str = String::from_utf8(plaintext)
        .map_err(|e| format!("Failed to convert decrypted message to string: {}", e))?;

    Ok(decrypted_message_str)
}
