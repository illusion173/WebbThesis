package com.webb;

public class Sha384ResponseMessage {
    private String signature;


    // Default constructor (required for Jackson)
    public Sha384ResponseMessage() {}

    public Sha384ResponseMessage(String signature) {
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
