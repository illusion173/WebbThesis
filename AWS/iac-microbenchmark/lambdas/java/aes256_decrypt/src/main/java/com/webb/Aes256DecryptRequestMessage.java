package com.webb;

public class Aes256DecryptRequestMessage {
    private String message;
    private String sender;

    // Default constructor (required for Jackson)
    public Aes256DecryptRequestMessage() {}

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
