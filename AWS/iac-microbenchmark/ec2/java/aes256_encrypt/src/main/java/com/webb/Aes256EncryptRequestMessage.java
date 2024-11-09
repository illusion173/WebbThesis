package com.webb;

public class Aes256EncryptRequestMessage{
    private String message;


    // Default constructor (required for Jackson)
    public Aes256EncryptRequestMessage() {}

    // Constructor with parameters for new fields
    public Aes256EncryptRequestMessage(String message) {
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
