package com.webb;

public class Sha256ResponseMessage {
    private String signature;


    // Default constructor (required for Jackson)
    public Sha256ResponseMessage() {}

    public Sha256ResponseMessage(String signature) {
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
