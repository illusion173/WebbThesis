package com.webb;

public class Ecc384VerifyRequestMessage {
    private String message;
    private String sender;

    // Default constructor (required for Jackson)
    public Ecc384VerifyRequestMessage() {}

    // Getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getSender() {
        return sender;
    }

    public void setSender(String sender) {
        this.sender = sender;
    }
}