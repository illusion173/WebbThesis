package com.webb;

public class Ecc384SignRequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Ecc384SignRequestMessage() {}

    // Getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

}
