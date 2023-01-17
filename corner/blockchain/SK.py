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

    def sign(self, data: bytes) -> Signature:
        """
        Generates a Signature for the given data.

        :param data: bytes
        :return: Signature
        """
        return Signature(self._sk.sign(pycryptonight.cn_fast_hash(data)),
                         self.vk)

    @property
    def raw(self) -> str:
        """
        Raw representation of SK based on the Discorn Protocol.

        :return: bytes
        """
        return self._sk.to_string()

    def from_raw(raw: bytes) -> SK:
        """
        Decodes a raw Signing Key.

        :param raw: bytes
        :return: SK
        """
        return SK(ecdsa.SigningKey.from_string(raw))

