package com.webb;

public class Rsa2048DecryptResponseMessage {
    private String message;
    private String sender;
    private String status;

    // Default constructor (required for Jackson)
    public Rsa2048DecryptResponseMessage() {}

    public Rsa2048DecryptResponseMessage(String message, String sender, String status) {
        this.message = message;
        this.sender = sender;
        this.status = status;
    }

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

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
