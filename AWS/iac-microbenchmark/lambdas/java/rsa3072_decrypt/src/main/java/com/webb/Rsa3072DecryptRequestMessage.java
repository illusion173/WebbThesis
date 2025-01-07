package com.webb;
import com.fasterxml.jackson.annotation.JsonProperty;

public class Rsa3072DecryptRequestMessage {
	  	private String ciphertext;
	    private String iv;
	    @JsonProperty("encrypted_aes_key")
	    private String encrypted_aes_key;
	    
	    public  Rsa3072DecryptRequestMessage() {}
	    
	    public  Rsa3072DecryptRequestMessage(String ciphertext, String iv, String encrypted_aes_key) {
	        this.ciphertext = ciphertext;
	        this.iv = iv;
	        this.encrypted_aes_key = encrypted_aes_key;
	    }
	    
	    
	    // Getter and Setter for ciphertext
	    public String getCiphertext() {
	        return ciphertext;
	    }


	    public void setCiphertext(String ciphertext) {
	        this.ciphertext = ciphertext;
	    }

	    // Getter and Setter for iv
	    public String getIv() {
	        return iv;
	    }

	    public void setIv(String iv) {
	        this.iv = iv;
	    }

	    // Getter and Setter for encrypted_aes_key
	    public String getEncryptedAesKey() {
	        return encrypted_aes_key;
	    }

	    public void setEncryptedAesKey(String encrypted_aes_key) {
	        this.encrypted_aes_key = encrypted_aes_key;
	    }
}
