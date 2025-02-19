package com.webb;

public class ecc384_signResponseMessage {

    private String signature;
    
    // Default constructor (required for Jackson)

    public ecc384_signResponseMessage() {}
    public ecc384_signResponseMessage(String signature) {
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
