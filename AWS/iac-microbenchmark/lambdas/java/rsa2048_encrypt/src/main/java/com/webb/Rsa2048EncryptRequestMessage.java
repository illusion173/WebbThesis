package com.webb;

public class Rsa2048EncryptRequestMessage {
    private String message;
    private String sender;

    // Default constructor (required for Jackson)
    public Rsa2048EncryptRequestMessage() {}

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
