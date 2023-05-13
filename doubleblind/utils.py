import base64
import mimetypes
import os
from typing import Tuple

import smaz
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

mimetypes.init()
BLOCK_SIZE = 16


def pad(plaintext):
    padding_len = BLOCK_SIZE - len(plaintext) % BLOCK_SIZE
    padding = bytes([padding_len] * padding_len)
    return plaintext + padding


def compress_if_shorter(text: str) -> Tuple[bytes, bool]:
    compressed = smaz.compress(text)
    encoded = text.encode()
    if len(compressed) < len(encoded):
        return compressed, True
    return encoded, False


def decompress(b: bytes):
    return smaz.decompress(b)


def unpad(padded):
    padding_len = padded[-1]
    return padded[:-padding_len]


def encode_filename(plaintext):
    # key is constant to reduce filename length
    key = b'\x0cm\xa3\xf7\x1e\xd4\x8f\xce\xb5& \xe4\xa4\xeaE\xcd\xaf\x80V\x7f_\x19\xce\xc7}\xa7-\xc6\x91\xc6\xbe~'
    text, is_compressed = compress_if_shorter(plaintext)
    padded = pad(text)
    iv = os.urandom(16)
    cipher_obj = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher_obj.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    slugified = base64.urlsafe_b64encode(iv + ciphertext).decode('ascii').rstrip('=')
    return slugified + ('C' if is_compressed else 'R')


def decode_filename(ciphertext):
    # key is constant to reduce filename length
    key = b'\x0cm\xa3\xf7\x1e\xd4\x8f\xce\xb5& \xe4\xa4\xeaE\xcd\xaf\x80V\x7f_\x19\xce\xc7}\xa7-\xc6\x91\xc6\xbe~'
    is_compressed = ciphertext.endswith('C')
    ciphertext = ciphertext[:-1]
    ciphertext += '=' * (-len(ciphertext) % 4)
    ciphertext = base64.urlsafe_b64decode(ciphertext.encode('ascii'))
    iv = ciphertext[:16]
    cipher_obj = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher_obj.decryptor()
    padded_plaintext = (decryptor.update(ciphertext[16:]) + decryptor.finalize())
    plaintext = decompress(unpad(padded_plaintext)) if is_compressed else unpad(padded_plaintext).decode()
    return plaintext


def get_extensions_for_type(general_type) -> str:
    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext
