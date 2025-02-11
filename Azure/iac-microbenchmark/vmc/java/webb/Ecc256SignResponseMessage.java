package com.webb;

public class Ecc256SignResponseMessage {
    private String signature;

    // Default constructor (required for Jackson)
    public Ecc256SignResponseMessage() {}

    public Ecc256SignResponseMessage(String signature) {
        this.signature = signature;
    }

    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }
}
