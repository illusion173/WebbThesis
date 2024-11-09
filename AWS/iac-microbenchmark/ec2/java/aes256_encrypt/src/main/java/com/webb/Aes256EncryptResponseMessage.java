package com.webb;

public class Aes256EncryptResponseMessage {
    private String ciphertext;
    private String iv;
    private String tag;
    private String encrypted_key;

    // Default constructor (required for Jackson)
    public Aes256EncryptResponseMessage() {}

    // Constructor with parameters for new fields
    public Aes256EncryptResponseMessage(String ciphertext, String iv, String tag, String encrypted_key) {
        this.ciphertext = ciphertext;
        this.iv = iv;
        this.tag = tag;
        this.encrypted_key = encrypted_key;
    }

    // Getters and setters for the new fields
    public String getCiphertext() {
        return ciphertext;
    }

    public void setCiphertext(String ciphertext) {
        this.ciphertext = ciphertext;
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

    public String getEncrypted_key() {
        return encrypted_key;
    }

    public void setEncrypted_key(String encrypted_key) {
        this.encrypted_key = encrypted_key;
    }
}
