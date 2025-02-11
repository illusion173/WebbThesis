package com.webb;

public class Ecc256SignRequestMessage {
    private String messageDigest;

    // Default constructor (required for Jackson)
    public Ecc256SignRequestMessage() {}

    public Ecc256SignRequestMessage(String messageDigest) {
        this.messageDigest = messageDigest;
    }

    public String getMessageDigest() {
        return messageDigest;
    }

    public void setMessageDigest(String messageDigest) {
        this.messageDigest = messageDigest;
    }
}
