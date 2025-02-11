package com.webb;

public class Rsa4096DecryptResponseMessage {
    private String message;

    // Default constructor (required for Jackson)
    public Rsa4096DecryptResponseMessage() {}

    public Rsa4096DecryptResponseMessage(String message) {
        this.message = message;
    }

    public String getmessage() {
        return message;
    }

    public void setmessage(String message) {
        this.message = message;
    }

}
