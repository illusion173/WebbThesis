package com.webb;

public class Rsa4096EncryptRequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa4096EncryptRequestMessage() {}

    public Rsa4096EncryptRequestMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}
