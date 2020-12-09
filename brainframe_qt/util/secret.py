from Cryptodome.Cipher import AES

NUNYA = "8ef03fe56e8326e5e82a56e90b09f411"
"""Exactly what it looks like"""


def encrypt(data_to_encrypt: str) -> bytes:
    """Encrypt the given source to dest.

    :param data_to_encrypt: The data to encode0
    """
    data = data_to_encrypt.encode('utf-8')
    cipher = AES.new(NUNYA.encode('utf-8'), AES.MODE_EAX)

    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)

    return nonce + tag + ciphertext


def decrypt(source: bytes) -> str:
    """Decrypt the given source into bytes.

    :param source: A file-like object to read from
    :return: The resulting bytes
    """

    nonce = source[:16]
    tag = source[16:32]
    ciphertext = source[32:]

    cipher = AES.new(NUNYA.encode("utf-8"), AES.MODE_EAX, nonce)

    return cipher.decrypt_and_verify(ciphertext, tag).decode()
