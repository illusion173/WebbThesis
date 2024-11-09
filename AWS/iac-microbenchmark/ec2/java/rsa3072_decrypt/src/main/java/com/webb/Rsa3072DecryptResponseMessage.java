package com.webb;

public class Rsa3072DecryptResponseMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa3072DecryptResponseMessage() {}

    public Rsa3072DecryptResponseMessage(String message) {
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
