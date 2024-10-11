package com.webb;

public class Rsa4096DecryptResponseMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa4096DecryptResponseMessage() {}

    public Rsa4096DecryptResponseMessage(String message) {
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
