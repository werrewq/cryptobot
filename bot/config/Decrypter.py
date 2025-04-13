from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

class Decrypter:
    __key: bytes

    def __init__(self, key):
        self.__key = key # .encode("windows-1252")

    def decrypt(self, encrypted_text: str):
        encrypted_data = base64.b64decode(encrypted_text.encode())
        iv = encrypted_data[:16]
        cipher = Cipher(algorithms.AES(self.__key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_text = decryptor.update(encrypted_data[16:]) + decryptor.finalize()
        return decrypted_text.decode()