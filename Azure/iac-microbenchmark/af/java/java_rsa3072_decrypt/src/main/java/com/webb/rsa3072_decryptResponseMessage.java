package com.webb;

public class rsa3072_decryptResponseMessage {
    private String message;

    // Default constructor (required for Jackson)
    public rsa3072_decryptResponseMessage() {}

    public rsa3072_decryptResponseMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}

