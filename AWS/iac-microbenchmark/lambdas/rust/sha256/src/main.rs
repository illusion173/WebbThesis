//use lambda_http::{run, service_fn, tracing, Body, Error, Request, RequestExt, Response};
use aws_sdk_kms::{self as kms, primitives::Blob};

use base64::encode;
use lambda_http::{run, service_fn, tracing, Body, Error, Request, RequestExt, Response};
use serde::{de::Error, Deserialize, Serialize};
use serde_json::{json, Value};
use std::env;

#[derive(Serialize, Deserialize, Debug)]
struct MessageStruct {
    message: String,
}

async fn function_handler(event: Request) -> Result<Response<Body>, Error> {
    // Get the KMS key ARN from environment variables
    let sha_kms_key_id =
        env::var("SHA256_KMS_KEY_ARN").map_err(|_| Error::from("KMS key ARN not set"))?;

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
                .body(Body::from(
                    "Invalid Request Body, missing message.",
                ))
                .expect("Failed to build a response."))
        }
    };

    // Convert the message to bytes
    let message_blob = Blob::new(message_struct.message.as_bytes());
    //let message_blob = Blob::new(message_bytes);

    // Initialize the KMS client
    let config = aws_config::load_from_env().await;

    let kms_client = kms::Client::new(&config);

    // Attempt to sign the message using KMS
    match kms_sign_message(&kms_client, &sha_kms_key_id, message_blob).await {
        Ok(signature) => {
            let response_body = json!({
                "signature": signature
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
            .body(format!("Error signing message: {}", e).into())?),
    }
}

/// Function to sign a message using AWS KMS.
async fn kms_sign_message(
    kms_client: &kms::Client,
    key_id: &str,
    message: Blob,
) -> Result<String, Error> {
    //let sign_output = kms_client.si
    //
    let mac_output = kms_client
        .generate_mac()
        .key_id(key_id)
        .message(message)
        .mac_algorithm(aws_sdk_kms::types::MacAlgorithmSpec::HmacSha256)
        .send()
        .await
        .map_err(|err| Error::from(format!("Failed to generate mac hash: {}", err)))?;

    let mac = mac_output
        .mac
        .ok_or_else(|| Error::from("No Mac hash returned"))?;

    Ok(encode(mac.as_ref()))
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing::init_default_subscriber();

    run(service_fn(function_handler)).await
}
