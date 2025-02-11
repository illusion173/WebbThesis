package com.webb;

public class Ecc384VerifyResponseMessage {
    private boolean is_valid;

    // Default constructor (required for Jackson)
    public Ecc384VerifyResponseMessage() {}

    public Ecc384VerifyResponseMessage(boolean is_valid) {
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
