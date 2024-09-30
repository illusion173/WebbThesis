use aws_sdk_kms::{self as kms, primitives::Blob};
use base64::encode;
use lambda_http::{run, service_fn, tracing, Body, Error, Request, RequestExt, Response};
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

    let encrypted_message_struct: EncryptedMessageStruct = match serde_json::from_str(body_str) {
        Ok(message_struct) => message_struct,
        Err(_error) => {
            return Ok(Response::builder()
                .header("Access-Control-Allow-Origin", "*")
                .status(400)
                .body(Body::from(
                    "Invalid Request Body, missing EncryptedMessageStruct props",
                ))
                .expect("Failed to build a response."))
        }
    };

    // Initialize the KMS client
    let config = aws_config::load_from_env().await;

    let kms_client = kms::Client::new(&config);

    // Attempt to sign the message using KMS
    match kms_decrypt_message(&kms_client, &aes_kms_key_id, encrypted_message_struct).await {
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
async fn kms_decrypt_message(
    kms_client: &kms::Client,
    key_id: &str,
    encrypted_message: EncryptedMessageStruct,
) -> Result<MessageStruct, Error> {
    // Decrypt the data key using KMS
    let encryption_key_decoded = decode(&encrypted_message.encrypted_key)
        .map(Blob::new)
        .map_err(|_| Error::from("Failed to decode encrypted key"))?;

    let data_key_output = kms_client
        .decrypt()
        .key_id(key_id)
        .ciphertext_blob(encryption_key_decoded)
        .send()
        .await
        .map_err(|err| Error::from(format!("Failed to decrypt data key: {}", err)))?;

    let plaintext_data_key = data_key_output
        .plaintext
        .ok_or_else(|| Error::from("No plaintext data key returned"))?;

    let plaintext_dk_u8 = plaintext_data_key.into_inner();

    // Decode the IV, tag, and ciphertext
    let iv = decode(&encrypted_message.iv).map_err(|_| Error::from("Failed to decode IV"))?;

    let tag = decode(&encrypted_message.tag).map_err(|_| Error::from("Failed to decode tag"))?;

    let ciphertext = decode(&encrypted_message.ciphertext)
        .map_err(|_| Error::from("Failed to decode ciphertext"))?;

    // AES-GCM decryption
    let cipher = openssl::symm::Cipher::aes_256_gcm();

    let decrypted_message =
        openssl::symm::decrypt_aead(cipher, &plaintext_dk_u8, Some(&iv), &[], &ciphertext, &tag)
            .map_err(|_| Error::from("AES Decryption failed"))?;

    let decrypted_message_struct = MessageStruct {
        message: String::from_utf8(decrypted_message).map_err(|_| Error::from("Invalid UTF-8"))?,
    };

    Ok(decrypted_message_struct)
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing::init_default_subscriber();

    run(service_fn(function_handler)).await
}
