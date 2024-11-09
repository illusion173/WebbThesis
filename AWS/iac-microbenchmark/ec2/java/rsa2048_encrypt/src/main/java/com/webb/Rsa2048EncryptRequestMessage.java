package com.webb;

public class Rsa2048EncryptRequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa2048EncryptRequestMessage() {}

    // Getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

}
