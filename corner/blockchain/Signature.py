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
    def raw(self) -> bytes:
        """
        Raw signature representation based on the Discorn Protocol.

        :return: bytes
        """
        return self.vk.raw + self.signature

    def verify(self, data: bytes) -> bool:
        """
        Verifies the Signature against data.

        :param data: bytes
        :return: bool
        """
        return self.vk.verify(self.signature, data)

    def from_raw(raw) -> Signature:
        """
        Decodes a raw Signature.

        :param raw: bytes
        :return: Signature
        """
        return Signature(raw[64:], VK.from_raw(raw[:64]))

