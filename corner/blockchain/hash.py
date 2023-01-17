
def fast_hash(data: bytes) -> str:
    """
    Hashing function used for Corner hashes.

    :param data: bytes
    :return: str
    """
    return pycryptonight.cn_fast_hash(data).hex()


def get_hash(data: bytes, hash_func=hashlib.sha256) -> bytes:
    """
    Hashing function used in key pairs.

    :param hash_func: function
    :param data: bytes
    :return: bytes
    """
    h = hash_func()
    h.update(data)
    return h.digest()
