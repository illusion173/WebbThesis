use aws_sdk_kms::{self as kms, primitives::Blob, Client};
use lambda_http::{run, service_fn, tracing, Body, Error, Request, Response};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::env;

#[derive(Serialize, Deserialize, Debug)]
struct ECC256Request {
    message: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct ECC256Response {
    signature: String,
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

    match kms_client_sign_message(&kms_client, &ecc_kms_key_id, &message).await {
        Ok(signature_struct) => {
            let response_body = json!(signature_struct);
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

async fn kms_client_sign_message(
    kms_client: &Client,
    key_id: &str,
    message: &str,
) -> Result<ECC256Response, Error> {

    let message_blob = Blob::new(message);
    let sign_output = kms_client
        .sign()
        .key_id(key_id)
        .message(message_blob)
        .message_type(aws_sdk_kms::types::MessageType::Raw)
        .signing_algorithm(aws_sdk_kms::types::SigningAlgorithmSpec::EcdsaSha256)
        .send()
        .await?;

    let signature = sign_output.signature().ok_or_else(|| Error::from("No Signature returned? ECC384 Sign"))?;

    // Encode the signature to base64
    let sig_b64 = base64::encode(signature);

    let signature_response = ECC256Response { signature: sig_b64 };

    Ok(signature_response)
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing::init_default_subscriber();

    run(service_fn(function_handler)).await
}

