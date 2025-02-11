use anyhow::Result;
use azure_security_keyvault::{prelude::SignatureAlgorithm, KeyClient};
use base64::encode;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine};
use hex::decode;
use serde::{Deserialize, Serialize};
use std::{env, io::Read, str::from_utf8};
use tokio;

#[derive(Deserialize)]
struct SignRequest {
    message_digest: String,
}

#[derive(Serialize)]
struct SignResponse {
    signature: String,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Read JSON input from command line arguments
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        eprintln!("Usage: sign '{{\"message_digest\":\"your_hash_here\"}}'");
        std::process::exit(1);
    }

    let input: SignRequest = serde_json::from_str(&args[1])?;

    let message_digest_hex_str = input.message_digest.clone();
    let digest_bytes = decode(message_digest_hex_str).expect("Invalid hex input");

    // Ensure it is exactly 32 bytes
    assert_eq!(digest_bytes.len(), 32, "Digest length is incorrect");

    // Convert bytes to base64url (no padding)
    let base64url_digest = URL_SAFE_NO_PAD.encode(digest_bytes);

    // Get Azure Key Vault details from environment variables
    let key_vault_url = env::var("AZURE_KEY_VAULT_URL")?;
    let key_name = env::var("ECC256_KEY_NAME")?;

    let credential = azure_identity::create_credential()?;

    // Authenticate and create Key Vault client
    let client = KeyClient::new(&key_vault_url, credential)?;
    let signature_result = client
        .sign(&key_name, SignatureAlgorithm::ES256, base64url_digest)
        .await?;

    let signature_vec = signature_result.signature;

    // Encode the signature in base64
    let response = SignResponse {
        signature: encode(signature_vec),
    };

    // Print the signature as JSON
    println!("{}", serde_json::to_string(&response)?);
    Ok(())
}
