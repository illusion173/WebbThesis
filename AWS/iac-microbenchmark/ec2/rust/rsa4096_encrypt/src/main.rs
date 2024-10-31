use aws_sdk_kms::{self as kms, primitives::Blob, Client};
use base64::encode;
use openssl::rand::rand_bytes;
use openssl::symm::{Cipher, Crypter, Mode};
use serde::{Deserialize, Serialize};
use std::env;
use std::error::Error;

#[derive(Serialize, Deserialize, Debug)]
struct RSA4096Request {
    message: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct RSA4096Response {
    ciphertext: String,
    iv: String,
    encrypted_key: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Get the KMS key ARN from environment variables
    let rsa_kms_key_id =
        env::var("RSA4096_KMS_KEY_ARN").map_err(|_| "RSA 4096 KMS key ARN not set?")?;

    // Get JSON input from command line
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        return Err("Usage: ./rustexecutable '{\"message\":\"your_message_here\"}'".into());
    }

    let body_str = &args[1];

    // Parse the input JSON
    let message_struct: RSA4096Request =
        serde_json::from_str(body_str).map_err(|_| "Invalid Request Body, missing message.")?;

    // Initialize the KMS client
    let kms_client = kms::Client::new(&aws_config::load_from_env().await);

    // Attempt to encrypt the message using KMS
    match aws_kms_rsa_encrypt(&kms_client, &rsa_kms_key_id, &message_struct.message).await {
        Ok(rsa_response) => {
            // Print the encrypted response
            println!("{}", serde_json::to_string(&rsa_response)?);
            Ok(())
        }
        Err(e) => Err(format!("Error encrypting message: {}", e).into()),
    }
}

async fn aws_kms_rsa_encrypt(
    kms_client: &Client,
    key_id: &str,
    message: &str,
) -> Result<RSA4096Response, Box<dyn Error>> {
    // Supply 32 bytes for AES key
    let mut aes_buf = [0; 32];
    rand_bytes(&mut aes_buf).map_err(|e| format!("Failed to generate AES key: {}", e))?;

    // Supply 16 bytes for IV
    let mut iv_buf = [0; 16];
    rand_bytes(&mut iv_buf).map_err(|e| format!("Failed to generate IV: {}", e))?;

    // Encrypt the message using AES-CTR
    let cipher = Cipher::aes_256_ctr();
    let mut crypter = Crypter::new(cipher, Mode::Encrypt, &aes_buf, Some(&iv_buf))
        .map_err(|e| format!("Failed to create Crypter: {}", e))?;

    // Do the physical encryption
    let mut ciphertext = vec![0; message.len() + cipher.block_size()];
    crypter
        .update(message.as_bytes(), &mut ciphertext)
        .map_err(|e| format!("Failed to encrypt message: {}", e))?;

    let count = crypter
        .finalize(&mut ciphertext)
        .map_err(|e| format!("Failed to finalize encryption: {}", e))?;

    ciphertext.truncate(count);

    // Encrypt the AES key using AWS KMS (RSA key encryption)
    let response = kms_client
        .encrypt()
        .key_id(key_id)
        .plaintext(Blob::new(aes_buf.to_vec())) // Encrypt the AES key
        .encryption_algorithm(kms::types::EncryptionAlgorithmSpec::RsaesOaepSha256)
        .send()
        .await
        .map_err(|err| format!("KMS encryption failed: {}", err))?;

    let encrypted_aes_key = response
        .ciphertext_blob()
        .expect("No CiphertextBlob in KMS response")
        .as_ref()
        .to_vec();

    // Step 5: Encode the ciphertext, IV, and encrypted AES key in base64
    let encoded_ciphertext = encode(&ciphertext);
    let encoded_iv = encode(&iv_buf);
    let encoded_encrypted_aes_key = encode(&encrypted_aes_key);

    // Return the response
    let rsa_response = RSA4096Response {
        ciphertext: encoded_ciphertext,
        iv: encoded_iv,
        encrypted_key: encoded_encrypted_aes_key,
    };

    Ok(rsa_response)
}
