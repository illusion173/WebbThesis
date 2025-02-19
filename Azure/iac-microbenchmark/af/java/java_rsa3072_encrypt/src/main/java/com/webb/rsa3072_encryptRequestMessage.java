package com.webb;

public class rsa3072_encryptRequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public rsa3072_encryptRequestMessage() {}

    public rsa3072_encryptRequestMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}
