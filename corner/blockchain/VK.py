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

    def verify(self, signature: bytes, data: bytes) -> bool:
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
    def raw(self) -> str:
        return self._vk.to_string()

    def from_raw(raw) -> VK:
        """
        Decodes a raw Verifying key

        :param raw: bytes
        :return: VK
        """
        return VK(ecdsa.VerifyingKey.from_string(raw,
                                                 curve=ecdsa.SECP256k1,
                                                 hashfunc=hashlib.sha256))
