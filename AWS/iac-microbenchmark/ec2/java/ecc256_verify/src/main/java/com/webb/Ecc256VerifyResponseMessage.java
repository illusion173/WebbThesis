package com.webb;

public class Ecc256VerifyResponseMessage {
    private boolean verified;

    // Default constructor (required for Jackson)
    public Ecc256VerifyResponseMessage() {}

    public Ecc256VerifyResponseMessage(boolean verified) {
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
