package com.webb;

public class Rsa2048EncryptRequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa2048EncryptRequestMessage() {}

    public Rsa2048EncryptRequestMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}
