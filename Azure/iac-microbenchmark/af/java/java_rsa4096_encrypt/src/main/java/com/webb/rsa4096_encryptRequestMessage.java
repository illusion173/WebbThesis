package com.webb;

public class rsa4096_encryptRequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public rsa4096_encryptRequestMessage() {}

    public rsa4096_encryptRequestMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}
