package com.webb;

public class Sha256RequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Sha256RequestMessage() {}

    // Getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
