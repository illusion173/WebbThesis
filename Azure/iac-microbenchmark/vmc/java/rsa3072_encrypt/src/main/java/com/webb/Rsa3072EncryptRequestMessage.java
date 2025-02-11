package com.webb;

public class Rsa3072EncryptRequestMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa3072EncryptRequestMessage() {}

    public Rsa3072EncryptRequestMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}
