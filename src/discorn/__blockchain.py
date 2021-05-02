import pycryptonight
import ecdsa
from Crypto.Hash import RIPEMD160
import hashlib
from log import Logger
import base58


def get_hash(data, hash_func=hashlib.sha256):
    h = hash_func()
    h.update(data)
    return h.digest()


class Input(Logger):
    def __init__(self, out_index, tx):
        self.tx = tx
        self.out_index = out_index
    
    def encode(self):
        return self.address + self.tx


class Output(Logger):
    def __init__(self, address, amount):
        self.address = address
        self.amount = amount

    def encode(self):
        return self.address + self.amount.to_bytes(8, 'big')


class SK(Logger):
    def __init__(self, sk=None):
        self._sk = sk
        if self._sk is None:
            self._sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        self._vk = self._sk.verifying_key
        self.vk = VK(self._vk)
        self.address = self.vk.address
        self.log("New address : " + self.address.hex())
    
    def sign(self, data):
        return self._sk.sign(pycryptonight.cn_fast_hash(data))


class VK(Logger):
    def __init__(self, vk):
        self._vk = vk
        self.string = self._vk.to_string()
        self.address = get_hash(pycryptonight.cn_fast_hash(self._vk.to_string()), RIPEMD160.new)
    
    def verify(self, signature, data):
        try:
            return self.vk.verify(signature, pycryptonight.cn_fast_hash(data))
        except ecdsa.keys.BadSignatureError:
            return False


class Signature(Logger):
    def __init__(self, signature, vk):
        self.signature = signature
        self.vk = vk

    def encode(self):
        res = self.vk.string + self.signature


class Tx(Logger):
    def __init__(self):
        self.version = (0).to_bytes(1, 'big')
        self.inputs = []
        self.outputs = []
        self.signatures = {}
        self.raw = self.encode_raw()
        self.flag = (0).to_bytes(1, 'big')
        self.payload = self.encode_payload()
    
    @property
    def in_value(self):
        val = 0
        for inp in self.inputs:
            val += inp.tx.outputs[inp.out_index].amount
        return val

    @property
    def out_value(self):
        val = 0
        for out in self.outputs:
            val += out.amount
        return val

    def encode_raw(self):
        res = self.version
        res += len(self.inputs).to_bytes(2, 'big')
        for inp in self.inputs:
            res += inp.encode()
        res += len(self.outputs).to_bytes(2, 'big')
        for out in self.outputs:
            res += out.encode()
        self.raw = res
        return res

    def sign(self, sk):
        if sk.address not in self.signatures:
            self.signatures.update({sk.address: {'signature': sk.sign(self.raw),
                                                 'vk': sk.vk}})

    def encode(self):
        res = self.encode_raw()
        for inp in self.inputs:
            res += self.signatures[inp.tx.outputs[inp.out_index]]
        return res

    def encode_payload(self):
        raw = self.encode()
        self.payload = len(raw).to_bytes(4, 'big') + self.flag + raw
        return self.payload

    def hash(self):
        return pycryptonight.cn_fast_hash(self.encode_corner())


class Corner(Logger):
    def __init__(self, flag, payload):
        self.flag = flag
        self.payload = payload

    def encode(self):
        return len(self.payload.payload).to_bytes(4, 'big') + self.flag + self.payload.payload


class Block(Logger):
    def __init__(self, previous_hash):
        self.version = (0).to_bytes(1, 'big')
        self.merkle_root = pycryptonight.cn_fast_hash(b'')
        self.previous_hash = previous_hash
        self.nonce = (0).to_bytes(4, 'big')
        self.header = self.encode_header()

    def encode_header(self):
        res = self.version + self.merkle_root + self.previous_hash + self.nonce
        self.header = len(res).to_bytes(8, 'big') + res
        return self.header

    def hash(self):
        return pycryptonight.cn_slow_hash(self.header, 4)


class BlockChain(Logger):
    
    def __init__(self):
        self.blocks = [b'']
        self.corners = {}
        self.unconfirmed_corners = {}


if __name__ == '__main__':
    SK()
