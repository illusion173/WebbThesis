use aws_sdk_kms::{self as kms, primitives::Blob, Client};
use base64::encode;
use lambda_http::{run, service_fn, tracing, Body, Error, Request, RequestExt, Response};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::env;
use openssl::rand::rand_bytes;
#[derive(Serialize, Deserialize, Debug)]
struct RSA2048Request {
    message: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct RSA2048Response {
    ciphertext: String,
    iv: String,
    encrypted_key: String,
}

async fn function_handler(event: Request) -> Result<Response<Body>, Error> {
    // Get the KMS key ARN from environment variables
    let rsa_kms_key_id = env::var("RSA2048_KMS_KEY_ARN")
        .map_err(|_| Error::from("RSA 2048 KMS key ARN not set?"))?;

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

    let message_struct: RSA2048Request = match serde_json::from_str(body_str) {
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
) -> Result<RSA2048Response, Error> {

    //Supply 32 bytes for aes key 
    let mut aes_buf = [0; 32];
    rand_bytes(&mut aes_buf).unwrap();

    // Supply 32 bytes for iv
    let mut iv_buf = [0;32];
    rand_bytes(&mut iv_buf).unwrap();




    let rsa_response = RSA2048Response {
        ciphertext: "test".to_string(),
        iv: "test".to_string(),
        encrypted_key: "test".to_string(),
    };




    Ok(rsa_response)
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing::init_default_subscriber();

    run(service_fn(function_handler)).await
}
