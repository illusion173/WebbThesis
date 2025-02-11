package com.webb;

public class Rsa2048DecryptResponseMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa2048DecryptResponseMessage() {}

    public Rsa2048DecryptResponseMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}

