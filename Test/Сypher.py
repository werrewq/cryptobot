from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64

def generate_key():
    return os.urandom(32)  # 32 байта = 256 бит

def encrypt(plain_text, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_text = encryptor.update(plain_text.encode()) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_text).decode()

def decrypt(encrypted_text, key):
    encrypted_data = base64.b64decode(encrypted_text.encode())
    iv = encrypted_data[:16]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_text = decryptor.update(encrypted_data[16:]) + decryptor.finalize()
    return decrypted_text.decode()

if __name__ == "__main__":
    original_text = "Барсучий жир 12345"

    key = generate_key()  # Генерация ключа
    print(f"Key: {key}")
    print(f"Original: {original_text}")

    encrypted_text = encrypt(original_text, key)
    print(f"Encrypted: {encrypted_text}")

    decrypted_text = decrypt(encrypted_text, key)
    print(f"Decrypted: {decrypted_text}")