package com.webb;

public class rsa4096_decryptResponseMessage {
    private String message;

    // Default constructor (required for Jackson)
    public rsa4096_decryptResponseMessage() {}

    public rsa4096_decryptResponseMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}

