import base64
import mimetypes
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

mimetypes.init()
BLOCK_SIZE = 16


def pad(plaintext):
    padding_len = BLOCK_SIZE - len(plaintext) % BLOCK_SIZE
    padding = bytes([padding_len] * padding_len)
    return plaintext + padding


def unpad(padded):
    padding_len = padded[-1]
    return padded[:-padding_len]


def encode_filename(plaintext):
    padded = pad(plaintext.encode('ascii'))
    key = os.urandom(32)
    iv = os.urandom(16)
    cipher_obj = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher_obj.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    slugified = base64.urlsafe_b64encode(key + iv + ciphertext).decode('ascii').rstrip('=')
    return slugified


def decode_filename(ciphertext):
    ciphertext += '=' * (-len(ciphertext) % 4)
    ciphertext = base64.urlsafe_b64decode(ciphertext.encode('ascii'))
    key = ciphertext[:32]
    iv = ciphertext[32:48]
    cipher_obj = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher_obj.decryptor()
    padded_plaintext = (decryptor.update(ciphertext[48:]) + decryptor.finalize())
    plaintext = unpad(padded_plaintext).decode('ascii')
    return plaintext


def get_extensions_for_type(general_type) -> str:
    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext
