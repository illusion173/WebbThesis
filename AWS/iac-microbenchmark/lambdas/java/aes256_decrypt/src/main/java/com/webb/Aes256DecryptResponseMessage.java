package com.webb;

public class Aes256DecryptResponseMessage{
    private String message;


    // Default constructor (required for Jackson)
    public Aes256DecryptResponseMessage() {}

    // Constructor with parameters for new fields
    public Aes256DecryptResponseMessage(String message) {
        this.message = message;
    }

    // Getters and setters for the new fields
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
