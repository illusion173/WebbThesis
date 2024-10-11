package com.webb;

public class Rsa3072EncryptRequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa3072EncryptRequestMessage() {}

    // Getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

}
