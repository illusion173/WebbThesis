package com.webb;

public class Rsa3072DecryptRequestMessage {
    private String iv;
    private String ciphertext;
    private String encrypted_aes_key;

    // Default constructor (required for Jackson)
    public Rsa3072DecryptRequestMessage() {}

    public Rsa3072DecryptRequestMessage(String iv, String ciphertext, String encrypted_aes_key) {
        this.iv = iv;
        this.ciphertext = ciphertext;
        this.encrypted_aes_key = encrypted_aes_key;
    }

    public String getiv() {
        return iv;
    }

    public void setiv(String iv) {
        this.iv = iv;
    }

    public String getciphertext() {
        return ciphertext;
    }

    public void setciphertext(String ciphertext) {
        this.ciphertext = ciphertext;
    }

    public String getencrypted_aes_key() {
        return encrypted_aes_key;
    }

    public void setencrypted_aes_key(String encrypted_aes_key) {
        this.encrypted_aes_key = encrypted_aes_key;
    }
}
