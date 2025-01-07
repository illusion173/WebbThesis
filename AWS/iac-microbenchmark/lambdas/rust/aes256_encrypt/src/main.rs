use aws_sdk_kms::{self as kms, primitives::Blob};
use base64::encode;
use lambda_http::{run, service_fn, tracing, Body, Error, Request, Response};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::env;

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

async fn function_handler(event: Request) -> Result<Response<Body>, Error> {
    // Get the KMS key ARN from environment variables
    let aes_kms_key_id =
        env::var("AES_KMS_KEY_ARN").map_err(|_| Error::from("KMS key ARN not set"))?;

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

    let message_struct: MessageStruct = match serde_json::from_str(body_str) {
        Ok(message_struct) => message_struct,
        Err(_error) => {
            return Ok(Response::builder()
                .header("Access-Control-Allow-Origin", "*")
                .status(400)
                .body(Body::from("Invalid Request Body, missing message."))
                .expect("Failed to build a response."))
        }
    };

    // Convert the message to bytes
    let message_blob = Blob::new(message_struct.message.as_bytes());

    // Initialize the KMS client
    let config = aws_config::load_from_env().await;

    let kms_client = kms::Client::new(&config);

    // Attempt to sign the message using KMS
    match kms_encrypt_message(&kms_client, &aes_kms_key_id, message_blob).await {
        Ok(encrypted_message_strct) => {
            let response_body = json!(encrypted_message_strct);

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

/// Function to encrypt a message using AWS KMS. AES 256
async fn kms_encrypt_message(
    kms_client: &kms::Client,
    key_id: &str,
    message: Blob,
) -> Result<EncryptedMessageStruct, Error> {
    // Generate a data key using KMS
    let data_key_output = kms_client
        .generate_data_key()
        .key_id(key_id)
        .key_spec("AES_256".into())
        .send()
        .await
        .map_err(|err| Error::from(format!("Failed to generate data key: {}", err)))?;

    let plaintext_data_key = data_key_output
        .plaintext
        .ok_or_else(|| Error::from("No plaintext data key returned"))?;

    let plaintext_dk_u8 = plaintext_data_key.into_inner(); // Convert

    let encrypted_data_key = data_key_output
        .ciphertext_blob
        .ok_or_else(|| Error::from("No encrypted data key returned"))?;

    // Generate IV and tag for AES-GCM
    let mut iv = [0u8; 16]; // Initialize a 16-byte array for IV

    openssl::rand::rand_bytes(&mut iv).map_err(|_| Error::from("Failed to generate IV"))?;

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
    .map_err(|_| Error::from("AES Encryption failed"))?;

    // Create the encrypted message struct, with Base64-encoded values
    let encrypted_message_struct = EncryptedMessageStruct {
        ciphertext: encode(&ciphertext),
        iv: encode(&iv),
        tag: encode(&tag),
        encrypted_key: encode(&encrypted_data_key),
    };

    Ok(encrypted_message_struct)
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing::init_default_subscriber();

    run(service_fn(function_handler)).await
}
