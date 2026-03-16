import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from dotenv import load_dotenv

load_dotenv()

AES_KEY_RAW = os.getenv("AES_KEY")

AES_KEY=AES_KEY_RAW[:32].ljust(32,"0").encode("utf-8") # it forces aes key to become 32 and then encode as binary via utf-8

def encrypt_file(data: bytes)-> bytes:
    cipher=AES.new(AES_KEY,AES.MODE_CBC) # makes bytes to Cipher block chaining
    ct_bytes=cipher.encrypt(pad(data,AES.block_size))
    return cipher.iv +ct_bytes

def decrypt_file(data: bytes) -> bytes:
    iv=data[:16]
    ct= data[16:]
    cipher= AES.new(AES_KEY,AES.MODE_CBC,iv=iv)
    return unpad(cipher.decrypt(ct),AES.block_size)

def save_encrypted_file(plaintext: bytes, filepath: str)-> None:
    os.makedirs(os.path.dirname(filepath),exist_ok=True)
    encrypted=encrypt_file(plaintext)
    with open(filepath,"wb")as f:
        f.write(encrypted)

def load_decrypted_file(filepath: str)-> bytes:
    with open(filepath,"rb")as f:
        encrypted=f.read()
    return decrypt_file(encrypted)
