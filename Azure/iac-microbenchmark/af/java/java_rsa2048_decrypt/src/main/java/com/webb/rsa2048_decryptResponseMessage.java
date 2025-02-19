package com.webb;

public class rsa2048_decryptResponseMessage {
    private String message;

    // Default constructor (required for Jackson)
    public rsa2048_decryptResponseMessage() {}

    public rsa2048_decryptResponseMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}

