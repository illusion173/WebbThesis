use aws_sdk_kms::{self as kms, primitives::Blob, Client};
use base64::encode;
use lambda_http::{run, service_fn, tracing, Body, Error, Request, RequestExt, Response};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::env;

#[derive(Serialize, Deserialize, Debug)]
struct ECC256Request {
    message: String,
    signature: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct ECC256Response {
    valid: bool,
}

async fn function_handler(event: Request) -> Result<Response<Body>, Error> {
    // Get the KMS key ARN from environment variables
    let ecc_kms_key_id =
        env::var("ECC256_KMS_KEY_ARN").map_err(|_| Error::from("ECC 256 KMS key ARN not set?"))?;

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

    let message_struct: ECC256Request = match serde_json::from_str(body_str) {
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

    let signature = message_struct.signature;

    match kms_client_verify_message(&kms_client, &ecc_kms_key_id, &message, &signature).await {
        Ok(is_valid) => {
            let response_body = json!(is_valid);
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

async fn kms_client_verify_message(
    kms_client: &Client,
    key_id: &str,
    message: &str,
    signature_b64: &str,
) -> Result<ECC256Response, Error> {

    // Decode the base64-encoded signature
    let signature = base64::decode(signature_b64)
        .map_err(|_| Error::from("Failed to decode signature ECC384"))?;

    let signature_blob = Blob::new(signature);

    let message_blob = Blob::new(message.as_bytes());

    // Perform the verification
    let verify_output = kms_client
        .verify()
        .key_id(key_id)
        .message(message_blob)
        .message_type(aws_sdk_kms::types::MessageType::Raw)
        .signature(signature_blob)
        .signing_algorithm(aws_sdk_kms::types::SigningAlgorithmSpec::EcdsaSha256)
        .send()
        .await?;

    let is_valid = verify_output.signature_valid;

    let verify_response = ECC256Response { valid: is_valid };

    Ok(verify_response)
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing::init_default_subscriber();

    run(service_fn(function_handler)).await
}
