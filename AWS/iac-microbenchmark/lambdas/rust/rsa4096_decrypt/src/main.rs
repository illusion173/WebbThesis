use aws_sdk_kms::{self as kms, primitives::Blob, Client};
use base64::{decode, encode};
use lambda_http::{run, service_fn, tracing, Body, Error, Request, RequestExt, Response};
use openssl::symm::{Cipher, Crypter, Mode};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::env;

#[derive(Serialize, Deserialize, Debug)]
struct RSA4096DecryptRequest {
    ciphertext: String,
    iv: String,
    encrypted_key: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct RSA4096DecryptResponse {
    message: String,
}

async fn function_handler(event: Request) -> Result<Response<Body>, Error> {
    // Get the KMS key ARN from environment variables
    let rsa_kms_key_id = env::var("RSA4096_KMS_KEY_ARN")
        .map_err(|_| Error::from("RSA 4096 KMS key ARN not set?"))?;

    let body_str = match std::str::from_utf8(event.body().as_ref()) {
        Ok(body_str) => body_str,
        Err(_error) => {
            return Ok(Response::builder()
                .header("Access-Control-Allow-Origin", "*")
                .status(400)
                .body(Body::from("Unable to derive request body, utf-8 error?"))
                .expect("Failed to build a response"))
        }
    };

    let request_struct: RSA4096DecryptRequest = match serde_json::from_str(body_str) {
        Ok(request_struct) => request_struct,
        Err(_error) => {
            return Ok(Response::builder()
                .header("Access-Control-Allow-Origin", "*")
                .status(400)
                .body(Body::from("Invalid Request Body, missing data."))
                .expect("Failed to build a response."))
        }
    };

    let kms_client = kms::Client::new(&aws_config::load_from_env().await);

    match aws_kms_rsa_decrypt(&kms_client, &rsa_kms_key_id, request_struct).await {
        Ok(decrypted_message) => {
            let response_body = json!(RSA4096DecryptResponse {
                message: decrypted_message
            });
            Ok(Response::builder()
                .status(200)
                .header("Access-Control-Allow-Origin", "*")
                .header("content-type", "application/json")
                .body(response_body.to_string().into())?)
        }
        Err(e) => Ok(Response::builder()
            .header("Access-Control-Allow-Origin", "*")
            .status(500)
            .body(format!("Error decrypting message: {}", e).into())?),
    }
}

async fn aws_kms_rsa_decrypt(
    kms_client: &Client,
    key_id: &str,
    request: RSA4096DecryptRequest,
) -> Result<String, Error> {
    // Step 1: Decode the base64-encoded AES key, IV, and ciphertext
    let encrypted_aes_key = decode(&request.encrypted_key)
        .map_err(|e| Error::from(format!("Failed to decode encrypted_key: {}", e)))?;
    let iv = decode(&request.iv).map_err(|e| Error::from(format!("Failed to decode IV: {}", e)))?;
    let ciphertext = decode(&request.ciphertext)
        .map_err(|e| Error::from(format!("Failed to decode ciphertext: {}", e)))?;

    // Step 2: Decrypt the AES key using AWS KMS
    let response = kms_client
        .decrypt()
        .key_id(key_id)
        .ciphertext_blob(Blob::new(encrypted_aes_key)) // Decrypt the AES key
        .encryption_algorithm(kms::types::EncryptionAlgorithmSpec::RsaesOaepSha256)
        .send()
        .await
        .map_err(|err| Error::from(format!("KMS decryption failed: {}", err)))?;

    let decrypted_aes_key = response
        .plaintext()
        .expect("No Plaintext in KMS response")
        .as_ref()
        .to_vec();

    // Step 3: Decrypt the message using AES-256-CTR with OpenSSL
    let cipher = Cipher::aes_256_ctr();
    let mut crypter = Crypter::new(cipher, Mode::Decrypt, &decrypted_aes_key, Some(&iv))
        .map_err(|e| Error::from(format!("Failed to create Crypter: {}", e)))?;

    let mut decrypted_message = vec![0; ciphertext.len() + cipher.block_size()];
    crypter
        .update(&ciphertext, &mut decrypted_message)
        .map_err(|e| Error::from(format!("Failed to decrypt ciphertext: {}", e)))?;
    let count = crypter
        .finalize(&mut decrypted_message)
        .map_err(|e| Error::from(format!("Failed to finalize decryption: {}", e)))?;
    decrypted_message.truncate(count);

    // Convert decrypted message to string
    let decrypted_message_str = String::from_utf8(decrypted_message).map_err(|e| {
        Error::from(format!(
            "Failed to convert decrypted message to string: {}",
            e
        ))
    })?;

    Ok(decrypted_message_str)
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing::init_default_subscriber();

    run(service_fn(function_handler)).await
}
