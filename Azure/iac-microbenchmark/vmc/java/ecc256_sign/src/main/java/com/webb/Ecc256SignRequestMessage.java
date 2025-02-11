package com.webb;

public class Ecc256SignRequestMessage {
    private String message_digest;

    // Default constructor (required for Jackson)
    public Ecc256SignRequestMessage() {}

    public Ecc256SignRequestMessage(String message_digest) {
        this.message_digest = message_digest;
    }

    public String getmessage_digest() {
        return message_digest;
    }

    public void setmessage_digest(String message_digest) {
        this.message_digest = message_digest;
    }
}
