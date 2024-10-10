package com.webb;

public class Ecc384VerifyResponseMessage {
    private boolean verified;

    // Default constructor (required for Jackson)
    public Ecc384VerifyResponseMessage() {}

    public Ecc384VerifyResponseMessage(boolean verified) {
        this.verified = verified;

    }

    // Getters and setters
    public boolean getVerified() {
        return verified;
    }

    public void setVerified(boolean verified) {
        this.verified = verified;
    }


}
