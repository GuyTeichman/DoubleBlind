import pytest

from doubleblind.utils import *


@pytest.mark.parametrize('version,expected', [('3.0.0', [3, 0, 0]), ('0.1.3', [0, 1, 3]), ('2.0.5', [2, 0, 5])])
def test_parse_version(version, expected):
    assert parse_version(version) == expected


def test_pad():
    # Test padding a string with a length that is a multiple of the block size
    assert pad(b"abcdefgh") == b"abcdefgh" + bytes([8] * 8)

    # Test padding a string with a length that is not a multiple of the block size
    assert pad(b"abcdefghi") == b"abcdefghi" + bytes([7] * 7)


def test_unpad():
    padded_string = b"Hello, world!\x05\x05\x05\x05\x05"
    assert unpad(padded_string) == b"Hello, world!"


@pytest.mark.parametrize('text,compressed_truth,is_compressed_truth',
                         [
                             ("This is a test string that can benefit from compression",
                              smaz.compress("This is a test string that can benefit from compression"), True),
                             ('bad_str1to3_4', b'bad_str1to3_4', False)
                         ])
def test_compress_if_shorter(text, compressed_truth, is_compressed_truth):
    compressed, is_compressed = compress_if_shorter(text)
    assert is_compressed == is_compressed_truth
    assert compressed == compressed_truth


def test_decompress():
    compressed_text = smaz.compress("Hello, world!")
    assert decompress(compressed_text) == "Hello, world!"


# Helper function to generate a random string for testing
def generate_random_string(length):
    return os.urandom(length).hex()


@pytest.mark.parametrize(
    "plaintext",
    [
        "Short string",
        "A slightly longer string",
        generate_random_string(100),
        generate_random_string(1000),
        '',
        'string0_with-cHARActe129_39'
    ]
)
def test_encode_filename_decode_filename(plaintext):
    # Test encoding and decoding with parametrized plaintext
    encoded = encode_filename(plaintext)
    decoded = decode_filename(encoded)
    assert encoded != plaintext
    assert decoded == plaintext
    assert encoded[-1] in ['R', 'C']
