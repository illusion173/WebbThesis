package com.webb;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Aes256DecryptRequestMessage {
    @JsonProperty("encrypted_data_key")
    private String encryptedDataKey;
    @JsonProperty("encrypted_message")
    private String encryptedMessage;
    private String iv;
    private String tag;

    // Default constructor (required for Jackson)
    public Aes256DecryptRequestMessage() {}

    // Constructor with parameters for new fields
    public Aes256DecryptRequestMessage(String encryptedMessage, String iv, String tag, String encryptedDataKey) {
        this.encryptedMessage = encryptedMessage;
        this.iv = iv;
        this.tag = tag;
        this.encryptedDataKey = encryptedDataKey;
    }

    // Getters and setters
    public String getEncryptedMessage() {
        return encryptedMessage;
    }

    public void setEncryptedMessage(String encryptedMessage) {
        this.encryptedMessage = encryptedMessage;
    }

    public String getIv() {
        return iv;
    }

    public void setIv(String iv) {
        this.iv = iv;
    }

    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }

    public String getEncryptedDataKey() {
        return encryptedDataKey;
    }

    public void setEncryptedDataKey(String encryptedDataKey) {
        this.encryptedDataKey = encryptedDataKey;
    }
}
