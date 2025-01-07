use aws_sdk_kms::{self as kms, primitives::Blob, Client};
use base64::encode;
use lambda_http::{run, service_fn, tracing, Body, Error, Request, Response};
use openssl::rand::rand_bytes;
use openssl::symm::{Cipher, Crypter, Mode};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::env;

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

    let message_struct: RSA4096Request = match serde_json::from_str(body_str) {
        Ok(message_struct) => message_struct,
        Err(_error) => {
            return Ok(Response::builder()
                .header("Access-Control-Allow-Origin", "*")
                .status(400)
                .body(Body::from("Invalid Request Body, missing message."))
                .expect("Failed to build a response."))
        }
    };

    let kms_client = kms::Client::new(&aws_config::load_from_env().await);

    let message = message_struct.message;

    match aws_kms_rsa_encrypt(&kms_client, &rsa_kms_key_id, &message).await {
        Ok(aws_kms_rsa_struct) => {
            let response_body = json!(aws_kms_rsa_struct);
            Ok(Response::builder()
                .status(200)
                .header("Access-Control-Allow-Origin", "*")
                .header("content-type", "application/json")
                .body(response_body.to_string().into())?)
        }
        Err(e) => Ok(Response::builder()
            .header("Access-Control-Allow-Origin", "*")
            .status(500)
            .body(format!("Error encrypting message: {}", e).into())?),
    }
}

async fn aws_kms_rsa_encrypt(
    kms_client: &Client,
    key_id: &str,
    message: &str,
) -> Result<RSA4096Response, Error> {
    //Supply 32 bytes for aes key
    let mut aes_buf = [0; 32];
    rand_bytes(&mut aes_buf).unwrap();

    // Supply 32 bytes for iv
    let mut iv_buf = [0; 16];
    rand_bytes(&mut iv_buf).unwrap();

    // Encrypt the message using AES-CTR
    let cipher = Cipher::aes_256_ctr();

    let mut crypter = Crypter::new(cipher, Mode::Encrypt, &aes_buf, Some(&iv_buf))
        .map_err(|e| Error::from(format!("Failed to create Crypter: {}", e)))?;

    // Do the physical encryption
    let mut ciphertext = vec![0; message.len() + cipher.block_size()];

    crypter
        .update(message.as_bytes(), &mut ciphertext)
        .map_err(|e| Error::from(format!("Failed to encrypt message: {}", e)))?;

    let count = crypter
        .finalize(&mut ciphertext)
        .map_err(|e| Error::from(format!("Failed to finalize encryption: {}", e)))?;

    ciphertext.truncate(count);

    // Encrypt the AES key using AWS KMS (RSA key encryption)
    let response = kms_client
        .encrypt()
        .key_id(key_id)
        .plaintext(Blob::new(aes_buf.to_vec())) // Encrypt the AES key
        .encryption_algorithm(kms::types::EncryptionAlgorithmSpec::RsaesOaepSha256)
        .send()
        .await
        .map_err(|err| Error::from(format!("KMS encryption failed: {}", err)))?;

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

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing::init_default_subscriber();

    run(service_fn(function_handler)).await
}
