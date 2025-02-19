package com.webb;

public class ecc256_signRequestMessage {

    private String message_digest;

    // Default constructor (required for Jackson)
    public ecc256_signRequestMessage() {}
    public ecc256_signRequestMessage(String message_digest) {
    	
     this.message_digest = message_digest;
    }


    public String getmessage_digest() {
        return message_digest;
    }

    public void setmessage_digest(String message_digest) {
        this.message_digest = message_digest;
    }
}
