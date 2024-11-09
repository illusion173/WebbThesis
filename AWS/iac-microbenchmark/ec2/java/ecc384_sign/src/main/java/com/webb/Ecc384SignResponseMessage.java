package com.webb;

public class Ecc384SignResponseMessage {
    private String signature;


    // Default constructor (required for Jackson)
    public Ecc384SignResponseMessage() {}

    public Ecc384SignResponseMessage(String signature) {
        this.signature = signature;
        
    }

    // Getters and setters
    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }
}
