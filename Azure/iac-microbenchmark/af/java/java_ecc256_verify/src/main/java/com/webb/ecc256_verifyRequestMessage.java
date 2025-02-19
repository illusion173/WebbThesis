package com.webb;

public class ecc256_verifyRequestMessage {
    private String message_digest;
    private String signature;

    // Default constructor (required for Jackson)
    public ecc256_verifyRequestMessage() {}

    public ecc256_verifyRequestMessage(String message_digest, String signature) {
        this.message_digest = message_digest;
        this.signature = signature;
    }

    public String getmessage_digest() {
        return message_digest;
    }

    public void setmessage_digest(String message_digest) {
        this.message_digest = message_digest;
    }

    public String getsignature() {
        return signature;
    }

    public void setsignature(String signature) {
        this.signature = signature;
    }
}
