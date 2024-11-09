package com.webb;

public class Rsa4096DecryptRequestMessage {
	  	private String ciphertext;
	    private String iv;
	    private String encryptedKey;
	    
	    public  Rsa4096DecryptRequestMessage() {}
	    
	    public  Rsa4096DecryptRequestMessage(String ciphertext, String iv, String encryptedKey) {
	        this.ciphertext = ciphertext;
	        this.iv = iv;
	        this.encryptedKey = encryptedKey;
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

	    // Getter and Setter for encrypted_key
	    public String getEncryptedKey() {
	        return encryptedKey;
	    }

	    public void setEncryptedKey(String encryptedKey) {
	        this.encryptedKey = encryptedKey;
	    }
}
