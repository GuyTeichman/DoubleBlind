import requests
import base64
import json
import mimetypes
import os
from typing import Tuple

import smaz
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from doubleblind import __version__

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
    iv_base =b'\xecVswy\xd1\xb2\x13`\x06\xe6b'


    text, is_compressed = compress_if_shorter(plaintext)
    padded = pad(text)
    iv = iv_base + os.urandom(4)
    cipher_obj = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher_obj.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    slugified = base64.urlsafe_b64encode(iv[12:] + ciphertext).decode('ascii').rstrip('=')
    return slugified + ('C' if is_compressed else 'R')


def decode_filename(ciphertext):
    # key is constant to reduce filename length
    key = b'\x0cm\xa3\xf7\x1e\xd4\x8f\xce\xb5& \xe4\xa4\xeaE\xcd\xaf\x80V\x7f_\x19\xce\xc7}\xa7-\xc6\x91\xc6\xbe~'
    iv_base =b'\xecVswy\xd1\xb2\x13`\x06\xe6b'
    is_compressed = ciphertext.endswith('C')
    ciphertext = ciphertext[:-1]
    ciphertext += '=' * (-len(ciphertext) % 4)
    ciphertext = base64.urlsafe_b64decode(ciphertext.encode('ascii'))
    iv = iv_base + ciphertext[:4]
    cipher_obj = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher_obj.decryptor()
    padded_plaintext = (decryptor.update(ciphertext[4:]) + decryptor.finalize())
    plaintext = decompress(unpad(padded_plaintext)) if is_compressed else unpad(padded_plaintext).decode()
    return plaintext


def get_extensions_for_type(general_type) -> str:
    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext


def parse_version(version: str):
    split = version.split('.')
    return [int(i) for i in split]


def is_app_outdated():
    installed_version = parse_version(__version__)
    pypi_link = 'https://pypi.python.org/pypi/doubleblind/json'
    try:
        req = requests.get(pypi_link)
    except (ConnectionError, requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        return False
    if req.status_code != 200:
        return False
    newest_version = parse_version(json.loads(req.text)['info']['version'])
    if installed_version < newest_version:
        return True
    return False
