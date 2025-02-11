package com.webb;

public class Rsa3072DecryptResponseMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa3072DecryptResponseMessage() {}

    public Rsa3072DecryptResponseMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}
