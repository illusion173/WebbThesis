package com.webb;

public class Ecc384VerifyRequestMessage {
    private String signature;
    private String message;


    // Default constructor (required for Jackson)
    public Ecc384VerifyRequestMessage() {}

    public Ecc384VerifyRequestMessage(String signature, String message) {
        this.signature = signature;
        this.message = message;
    }

    // Getters and setters
    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }
    // Getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
