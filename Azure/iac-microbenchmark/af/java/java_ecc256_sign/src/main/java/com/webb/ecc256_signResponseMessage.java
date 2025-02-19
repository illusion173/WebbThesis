package com.webb;

public class ecc256_signResponseMessage {

    private String signature;
    
    // Default constructor (required for Jackson)

    public ecc256_signResponseMessage() {}
    public ecc256_signResponseMessage(String signature) {
    	this.signature = signature;	
    }

    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }

    // Getters and setters
}
