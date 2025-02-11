use anyhow::Result;
use azure_security_keyvault::{prelude::SignatureAlgorithm, KeyClient};
use base64::{decode, engine::general_purpose::URL_SAFE_NO_PAD, Engine};
use serde::{Deserialize, Serialize};
use std::{env, process};
use tokio;

#[derive(Deserialize)]
struct VerifyRequest {
    message_digest: String,
    signature: String,
}

#[derive(Serialize)]
struct VerifyResponse {
    is_verified: bool,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Read JSON input from command line arguments
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        eprintln!("Usage: verify '{{\"message_digest\":\"your_hash_here\", \"signature\":\"your_base64url_signature_here\"}}'");
        process::exit(1);
    }

    let input: VerifyRequest = serde_json::from_str(&args[1])?;

    // Convert hex message digest to bytes
    let message_digest_bytes = decode(&input.message_digest)?;
    if message_digest_bytes.len() != 32 {
        eprintln!(
            "Error: SHA-256 digest must be exactly 32 bytes, but got {} bytes",
            message_digest_bytes.len()
        );
        process::exit(1);
    }

    // Convert signature from base64url to bytes
    let signature_bytes = decode(&input.signature)?;

    // Get Azure Key Vault details from environment variables
    let key_vault_url = env::var("AZURE_KEY_VAULT_URL")?;
    let key_name = env::var("ECC256_KEY_NAME")?;

    // Create credentials and KeyClient
    let credential = azure_identity::create_credential()?;
    let client = KeyClient::new(&key_vault_url, credential)?;

    // Convert message digest to base64url encoding (for verification)
    let base64url_digest = URL_SAFE_NO_PAD.encode(message_digest_bytes);
    let verify_result = client

    // Verify the signature
    let verify_result = client
        .verify(
            &key_name,
            SignatureAlgorithm::ES256,
            base64url_digest,
            signature_bytes,
        )
        .await?;

    // Prepare the response indicating if verification was successful
    let response = VerifyResponse {
        is_verified: verify_result.is_verified,
    };

    // Print the verification result as JSON
    println!("{}", serde_json::to_string(&response)?);

    Ok(())
}
