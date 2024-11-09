package com.webb;

public class Rsa2048DecryptResponseMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa2048DecryptResponseMessage() {}

    public Rsa2048DecryptResponseMessage(String message) {
        this.message = message;
        
    }
    // Getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

}
