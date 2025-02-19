package com.webb;

public class rsa2048_encryptRequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public rsa2048_encryptRequestMessage() {}

    public rsa2048_encryptRequestMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}
