package com.webb;

public class ecc384_verifyResponseMessage {
    private boolean is_valid;

    // Default constructor (required for Jackson)
    public ecc384_verifyResponseMessage() {}

    public ecc384_verifyResponseMessage(boolean is_valid) {
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
