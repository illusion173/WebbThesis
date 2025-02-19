package com.webb;

public class ecc256_verifyResponseMessage {
    private boolean is_valid;

    // Default constructor (required for Jackson)
    public ecc256_verifyResponseMessage() {}

    public ecc256_verifyResponseMessage(boolean is_valid) {
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
