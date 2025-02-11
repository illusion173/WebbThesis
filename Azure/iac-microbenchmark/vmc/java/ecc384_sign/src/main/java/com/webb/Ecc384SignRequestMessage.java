package com.webb;

public class Ecc384SignRequestMessage {
    private String message_digest;

    // Default constructor (required for Jackson)
    public Ecc384SignRequestMessage() {}

    public Ecc384SignRequestMessage(String message_digest) {
        this.message_digest = message_digest;
    }

    public String getmessage_digest() {
        return message_digest;
    }

    public void setmessage_digest(String message_digest) {
        this.message_digest = message_digest;
    }
}
