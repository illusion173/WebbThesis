package com.webb;

public class Rsa4096EncryptRequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa4096EncryptRequestMessage() {}

    // Getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

}
