import pycryptonight
import ecdsa
from Crypto.Hash import RIPEMD160
import hashlib
from log import Logger
import base58
import os


class Block:
    """Block and header definition."""

    NONCE_SIZE = 64

    def __init__(self, version=0, corners=None, previous_hash=pycryptonight.cn_slow_hash(b''),
                 nonce=(0).to_bytes(NONCE_SIZE, 'big')):
        self.version = version
        self.merkle_root = pycryptonight.cn_fast_hash(b'')
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.corners = []  # index 0 is coinbase.
        self.header = self.encode_header()
        self.hash = self.get_hash()

    def encode_header(self):
        res = self.version.to_bytes(2, 'big')
        res += len(self.corners).to_bytes(3, 'big')
        res += self.merkle_root
        res += self.previous_hash
        res += self.nonce
        self.header = res
        return res

    def random_nonce(self):
        self.nonce = os.urandom(64)

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
        pass


if __name__ == '__main__':
    chain = BlockChain()
    genesis = Block()
    genesis.random_nonce()
    genesis.encode_header()
    genesis.get_hash()
    chain.new_head(genesis)
