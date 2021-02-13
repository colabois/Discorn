# TODO: Recode all of this once again.

import pycryptonight
import ecdsa
from Crypto.Hash import RIPEMD160
import hashlib
from log import Logger
import base58
import os
import time
import string
from merklelib import MerkleTree


def fast_hash(b):
    return pycryptonight.cn_fast_hash(b).hex()


def get_hash(data, hash_func=hashlib.sha256):
    h = hash_func()
    h.update(data)
    return h.digest()


class SK:
    def __init__(self, sk=None):
        self._sk = sk
        if self._sk is None:
            self._sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        self._vk = self._sk.verifying_key
        self.vk = VK(self._vk)
        self.address = self.vk.address
        self.b58 = base58.b58encode(self.address, base58.BITCOIN_ALPHABET)

    def sign(self, data):
        return Signature(self._sk.sign(pycryptonight.cn_fast_hash(data)), self.vk)


class VK:
    def __init__(self, vk):
        self._vk = vk
        self.string = self._vk.to_string()
        self.address = get_hash(pycryptonight.cn_fast_hash(self._vk.to_string()), RIPEMD160.new)
        self.b58 = base58.b58encode(self.address, base58.BITCOIN_ALPHABET)

    def verify(self, signature, data):
        try:
            return self.vk.verify(signature.signature, pycryptonight.cn_fast_hash(data))
        except ecdsa.keys.BadSignatureError:
            return False


class Signature(Logger):
    def __init__(self, signature, vk):
        self.signature = signature
        self.vk = vk

    @property
    def raw(self):
        return self.vk.string + self.signature


class Corner:
    def __init__(self, flag=-1):
        self.flag = flag
        self.payload = b''

    @property
    def raw(self):
        res = len(self.payload).to_bytes(2, 'big')
        res += self.flag.to_bytes(1, 'big')
        res += self.payload
        return res


class Tx(Corner):
    def __init__(self, version=0, inputs=None, outputs=None, signatures=None):
        self.flag = 0
        self.version = version
        self.inputs = [] if inputs is None else inputs
        self.outputs = [] if outputs is None else outputs
        self.signatures = [] if signatures is None else signatures

    @property
    def body(self):
        res = self.version.to_bytes(1, 'big')
        res += len(self.inputs).to_bytes(1)
        for (address, origin) in self.inputs:
            res += address + origin
        res += len(self.outputs)
        for (address, amount) in self.outputs:
            res += address + amount.to_bytes()

    @property
    def payload(self):
        res = self.body
        for signature in self.signatures:
            res += signature.raw
        return res


class Authority:
    def __init__(self, parent=None):
        self.parent = parent


class PoW(Authority):
    def __init__(self, parent=None, last_hash=pycryptonight.cn_slow_hash(b''), nonce=0):
        super().__init__(parent)
        self.last_hash = last_hash
        self.nonce = nonce


class Event(Corner):
    authority = b''

    def __init__(self, version=0, event_hash=pycryptonight.cn_fast_hash(b'')):
        self.flag = 1
        self.version = version
        self.event_hash = event_hash
        self.authority_flag = -1

    @property
    def payload(self):
        res = self.version.to_bytes(1, 'big')
        res += self.event_hash
        res += self.authority_flag(1, 'big')
        res += self.authority


class Block(Logger):
    """Block and header definition."""

    NONCE_SIZE = 4

    def __init__(self,
                 blockchain=None,
                 name='block',
                 height=0,
                 version=0,
                 coinbase=None,
                 corners=None,
                 timestamp=0,
                 previous_hash=pycryptonight.cn_slow_hash(b''),
                 nonce=(0).to_bytes(NONCE_SIZE, 'big')):
        super().__init__(f"{name} - {height} :")
        self.blockchain = blockchain
        self.version = version
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.coinbase = coinbase
        self._corners = [] if corners is None else corners
        self.merkle_tree = MerkleTree(self.corners, fast_hash)
        self.hash = self.get_hash()
        self.difficulty = 4

    @property
    def corners(self):
        return [self.coinbase] + self._corners

    def compute_tree(self, new_data=None):
        if new_data is None:
            self.merkle_tree = MerkleTree(self.corners, fast_hash)
        else:
            self.merkle_tree.extend(new_data)

    @property
    def header(self):
        res = self.version.to_bytes(2, 'big')
        res += self.timestamp.to_bytes(8, 'big')
        res += len(self.corners).to_bytes(3, 'big')
        res += bytes.fromhex(self.merkle_tree.merkle_root)
        res += self.previous_hash
        res += self.nonce
        return res

    def random_nonce(self):
        self.timestamp = time.time_ns()
        self.nonce = os.urandom(self.NONCE_SIZE)

    def mine(self, difficulty=None):
        difficulty = self.difficulty if difficulty is None else difficulty
        while int.from_bytes(self.get_hash(), 'big') >= (1 << (256 - difficulty)):
            self.log(f"new hash : {self.hash.hex()}")
            self.random_nonce()
        self.log(f"Mined !! : {self.hash.hex()}")

    def get_hash(self):
        self.hash = pycryptonight.cn_slow_hash(self.header, 4)
        return self.hash


class BlockChain(Logger):
    """BlockChain data model."""

    def __init__(self, name='Main'):
        super().__init__(name)
        self.block_hashes = []
        self.blocks = {}
        self.corners = {}
        self.unconfirmed_corners = {}

    def new_head(self, block):
        self.block_hashes.append(block.hash)
        self.blocks.update({block.hash: block})
        self.log(f"New head : [{len(self.blocks)}] - {block.hash.hex()}")

    def get_block_template(self):
        block = Block(self,
                      corners=[corner for corner in self.unconfirmed_corners.items()],
                      timestamp=time.time_ns(),
                      previous_hash=self.block_hashes[-1])

    def check_tx(self, tx):  # TODO: Check that the fee is positive ; Inputs exist and are not spent ;
        pass

    def check_block(self, block):  # TODO: * Check output value for Coinbase and check every other Corner
        res = block.previous_hash in self.blocks
        res = res and int.from_bytes(block.get_hash(), 'big') >= (1 << (256 - block.difficulty))
        return res


if __name__ == '__main__':
    chain = BlockChain()
    genesis = Block(chain, name='Main')
    genesis.random_nonce()
    genesis.get_hash()
    chain.new_head(genesis)
