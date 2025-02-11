package com.webb;

public class Ecc256VerifyResponseMessage {
    private boolean is_valid;

    // Default constructor (required for Jackson)
    public Ecc256VerifyResponseMessage() {}

    public Ecc256VerifyResponseMessage(boolean is_valid) {
    	this.is_valid = is_valid;
    }

    // Getters and setters
    public boolean getis_valid() {
        return this.is_valid;
    }

    public void setis_valid(boolean is_valid) {
        this.is_valid = is_valid;
    }
}
