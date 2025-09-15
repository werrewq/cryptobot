from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64

from bot.config.Decrypter import Decrypter

def generate_key() -> bytes:
    return os.urandom(32)  # 32 байта = 256 бит

def encrypt(plain_text, key) -> str:
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_text = encryptor.update(plain_text.encode()) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_text).decode()

def prepare_data(
        broker_api_key: str,
        broker_secret_key: str,
        telegram_bot_api_token: str,
        cryptobot_api_token: str,
):
    print("INPUT DATA:")
    print(f"BROKER_API_KEY={broker_api_key}")
    print(f"BROKER_SECRET_KEY={broker_secret_key}")
    print(f"TELEGRAM_BOT_API_TOKEN={telegram_bot_api_token}")
    print(f"CRYPTOBOT_API_TOKEN={cryptobot_api_token}")

    key = generate_key()  # Генерация ключа
    print(f"\nKey={key}")

    encrypted_broker_api_key = encrypt(broker_api_key, key)
    encrypted_broker_secret_key = encrypt(broker_secret_key, key)
    encrypted_telegram_bot_api_token = encrypt(telegram_bot_api_token, key)
    encrypted_cryptobot_api_token = encrypt(cryptobot_api_token, key)

    print("\nENCRYPTED DATA:")
    print(f"BROKER_API_KEY={encrypted_broker_api_key}")
    print(f"BROKER_SECRET_KEY={encrypted_broker_secret_key}")
    print(f"TELEGRAM_BOT_API_TOKEN={encrypted_telegram_bot_api_token}")
    print(f"CRYPTOBOT_API_TOKEN={encrypted_cryptobot_api_token}")

    decrypter = Decrypter(key)

    decrypted_broker_api_key = decrypter.decrypt(encrypted_broker_api_key)
    decrypted_broker_secret_key = decrypter.decrypt(encrypted_broker_secret_key)
    decrypted_telegram_bot_api_token = decrypter.decrypt(encrypted_telegram_bot_api_token)
    decrypted_cryptobot_api_token = decrypter.decrypt(encrypted_cryptobot_api_token)

    print("\nDECRYPTED DATA:")
    print(f"BROKER_API_KEY={decrypted_broker_api_key}")
    print(f"BROKER_SECRET_KEY={decrypted_broker_secret_key}")
    print(f"TELEGRAM_BOT_API_TOKEN={decrypted_telegram_bot_api_token}")
    print(f"CRYPTOBOT_API_TOKEN={decrypted_cryptobot_api_token}")

test_broker_api_key = "your_test_broker_api_key"
test_broker_secret_key = "your_test_broker_secret_key"
test_telegram_bot_api_token = "your_test_telegram_bot_api_token"
test_cryptobot_api_token = "your_test_cryptobot_api_token"

if __name__ == "__main__":
    prepare_data(
        broker_api_key=test_broker_api_key,
        broker_secret_key=test_broker_secret_key,
        telegram_bot_api_token=test_telegram_bot_api_token,
        cryptobot_api_token=test_cryptobot_api_token,
    )