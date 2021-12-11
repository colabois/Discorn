import ecdsa
import hashlib
import pycryptonight
from Crypto.Hash import RIPEMD160
import base58


def fast_hash(data: bytes):
    """
    Hashing function used for Corner hashes.

    :param data: bytes
    :return: str
    """
    return pycryptonight.cn_fast_hash(data).hex()


def get_hash(data: bytes, hash_func=hashlib.sha256):
    """
    Hashing function used in key pairs.

    :param hash_func: function
    :param data: bytes
    :return: bytes
    """
    h = hash_func()
    h.update(data)
    return h.digest()


class SK:
    """Signing Key object"""

    def __init__(self, sk: ecdsa.SigningKey = None):
        """
        Generates a new Signing Key if sk is None.

        :type sk: ecdsa.SigningKey
        """
        self._sk = sk
        if self._sk is None:
            self._sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1,
                                                 hashfunc=hashlib.sha256)
        self._vk = self._sk.verifying_key
        self.vk = VK(self._vk)
        self.address = self.vk.address
        self.b58 = self.vk.b58

    def sign(self, data: bytes):
        """
        Generates a Signature for the given data.

        :param data: bytes
        :return: Signature
        """
        return Signature(self._sk.sign(pycryptonight.cn_fast_hash(data)),
                         self.vk)

    @property
    def raw(self):
        """
        Raw representation of SK based on the Discorn Protocol.

        :return: bytes
        """
        return self._sk.to_string()

    def from_raw(raw: bytes):
        """
        Decodes a raw Signing Key.

        :param raw: bytes
        :return: SK
        """
        return SK(ecdsa.SigningKey.from_string(raw))


class VK:
    """Verifying Key object"""

    def __init__(self, vk: ecdsa.VerifyingKey):
        """
        Initialise a Verifying Key instance.

        :param vk: ecdsa.VerifyingKey
        """
        self._vk = vk
        address = get_hash(pycryptonight.cn_fast_hash(self._vk.to_string()),
                           RIPEMD160.new)
        self.address = address + pycryptonight.cn_fast_hash(address)[:8]
        self.b58 = base58.b58encode(self.address, base58.BITCOIN_ALPHABET)

    def verify(self, signature: bytes, data: bytes):
        """
        Verifies raw signature.

        :param signature: bytes
        :param data: bytes
        :return: bool
        """
        try:
            return self._vk.verify(signature, pycryptonight.cn_fast_hash(data))
        except ecdsa.keys.BadSignatureError:
            return False

    @property
    def raw(self):
        return self._vk.to_string()

    def from_raw(raw):
        """
        Decodes a raw Verifying key

        :param raw: bytes
        :return: VK
        """
        return VK(ecdsa.VerifyingKey.from_string(raw,
                                                 curve=ecdsa.SECP256k1,
                                                 hashfunc=hashlib.sha256))


class Signature:
    """Signature object"""

    def __init__(self, signature: bytes, vk: VK):
        """
        Initialises a Signature instance.

        :param signature: bytes
        :param vk: VK
        """
        self.signature = signature
        self.vk = vk

    @property
    def raw(self):
        """
        Raw signature representation based on the Discorn Protocol.

        :return: bytes
        """
        return self.vk.raw + self.signature

    def verify(self, data: bytes):
        """
        Verifies the Signature against data.

        :param data: bytes
        :return: bool
        """
        return self.vk.verify(self.signature, data)

    def from_raw(raw):
        """
        Decodes a raw Signature.

        :param raw: bytes
        :return: Signature
        """
        return Signature(raw[64:], VK.from_raw(raw[:64]))


class Puzzle:
    def __init__(self):
        pass

    @property
    def raw(self):
        pass


class Single(Puzzle):
    pass

