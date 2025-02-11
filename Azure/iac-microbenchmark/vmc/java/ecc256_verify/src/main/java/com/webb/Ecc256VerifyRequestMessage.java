package com.webb;

public class Ecc256VerifyRequestMessage {
    private String message_digest;
    private String signature;

    // Default constructor (required for Jackson)
    public Ecc256VerifyRequestMessage() {}

    public Ecc256VerifyRequestMessage(String message_digest, String signature) {
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
