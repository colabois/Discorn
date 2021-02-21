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


def fast_hash(b: bytes):
    """Hashing function used for Corner hashes.
    :type b: bytes | data to hash
    :returns string | hexadecimal hash representation
    """
    return pycryptonight.cn_fast_hash(b).hex()


def get_hash(data: bytes, hash_func=hashlib.sha256):
    """Hashing function used in key pairs.
    :param hash_func: function | hash function that follows hashlib's way of hashing...
    :type data: bytes
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

        :type sk: object
        """
        self._sk = sk
        if self._sk is None:
            self._sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
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
        return Signature(self._sk.sign(pycryptonight.cn_fast_hash(data)), self.vk)


class VK:
    """Verifying Key object"""
    def __init__(self, vk: ecdsa.VerifyingKey):
        """
        Initialise a Verifying Key instance.

        :param vk: ecdsa.VerifyingKey
        """
        self._vk = vk
        self.string = self._vk.to_string()
        address = get_hash(pycryptonight.cn_fast_hash(self._vk.to_string()), RIPEMD160.new)
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
        Raw signature representation base on the Discorn Protocol.

        :return: bytes
        """
        return self.vk.string + self.signature

    def verify(self, data: bytes):
        """
        Verifies the Signature against data.

        :param data: bytes
        :return: bool
        """
        return self.vk.verify(self, data)


def raw_sig(raw):
    """
    Decodes a raw signature into a Signature object.

    :param raw: bytes
    :return: Signature
    """
    return Signature(raw[64:], ecdsa.VerifyingKey.from_string(raw[:64], curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256))


class Corner:
    """Corner object"""
    def __init__(self, flag=-1):
        """
        This function has to be overloaded.

        :param flag:
        """
        self.flag = flag

    @property
    def raw(self):
        """
        Raw representation of Corner based on Discorn Protocol.

        :return: bytes
        """
        res = len(self.payload).to_bytes(2, 'big')
        res += self.flag.to_bytes(1, 'big')
        res += self.payload
        return res

    @property
    def payload(self):
        """
        Raw payload.

        :return: bytes
        """
        return b''


class Tx(Corner):
    """Transaction object"""
    def __init__(self, version=0, inputs=None, outputs=None, signatures=None):
        """
        Initialise a transaction object.

        :param version: int
        :param inputs: Input list
        :param outputs: Output list
        :param signatures: Signature list
        """
        self.flag = 0
        self.version = version
        self.inputs = [] if inputs is None else inputs
        self.outputs = [] if outputs is None else outputs
        self.signatures = [] if signatures is None else signatures

    @property
    def body(self):
        """
        Raw representation of Transaction payload based on the Discorn Protocol (without signatures)

        :return: bytes
        """
        res = self.version.to_bytes(1, 'big')
        res += len(self.inputs).to_bytes(1)
        for (address, origin) in self.inputs:
            res += address + origin
        res += len(self.outputs)
        for (address, amount) in self.outputs:
            res += address + amount.to_bytes()

    @property
    def payload(self):
        """
        Raw representation of Transaction payload based on the Discorn Protocol

        :return: bytes
        """
        res = self.body
        for signature in self.signatures:
            res += signature.raw
        return res


class Block(Logger):
    """Block and header definition."""

    NONCE_SIZE = 4

    def __init__(self,
                 blockchain = None,
                 name: str = 'block',
                 height: int = 0,
                 version: int = 0,
                 coinbase: Corner = None,
                 corners: list = None,
                 timestamp=0,
                 previous_hash=pycryptonight.cn_slow_hash(b''),
                 nonce=(0).to_bytes(NONCE_SIZE, 'big')):
        """
        Initialises a Block instance.

        :param blockchain: Blockchain
        :param name: str
        :param height: int
        :param version: int
        :param coinbase: Corner
        :param corners: Corner list
        :param timestamp: int
        :param previous_hash: bytes
        :param nonce: bytes
        """
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
        """
        list of coinbase and other corners.

        :return: Corner list
        """
        return [self.coinbase] + self._corners

    def compute_tree(self, new_data=None):
        """
        Computes the Merkle Tree associated with the corners in the block.

        :param new_data: Corner list
        :return: None
        """
        if new_data is None:
            self.merkle_tree = MerkleTree(self.corners, fast_hash)
        else:
            self.merkle_tree.extend(new_data)

    @property
    def header(self):
        """
        Raw representation of block header based on the Discorn Protocol.

        :return: bytes
        """
        res = self.version.to_bytes(2, 'big')
        res += self.timestamp.to_bytes(8, 'big')
        res += len(self.corners).to_bytes(3, 'big')
        res += bytes.fromhex(self.merkle_tree.merkle_root)
        res += self.previous_hash
        res += self.nonce
        return res

    def random_nonce(self):
        """
        Generates a random nonce for this block. (Mining OP)

        :return: None
        """
        self.timestamp = time.time_ns()
        self.nonce = os.urandom(self.NONCE_SIZE)

    def mine(self, difficulty=None):
        """
        Mines the given block for the given difficulty.

        :param difficulty: int
        :return: None
        """
        difficulty = self.difficulty if difficulty is None else difficulty
        while int.from_bytes(self.get_hash(), 'big') >= (1 << (256 - difficulty)):
            self.log(f"new hash : {self.hash.hex()}")
            self.random_nonce()
        self.log(f"Mined !! : {self.hash.hex()}")

    def get_hash(self):
        """
        Calculates the block's hash.

        :return: bytes
        """
        self.hash = pycryptonight.cn_slow_hash(self.header, 4)
        return self.hash


class BlockChain(Logger):
    """BlockChain data model."""

    def __init__(self, name:str = 'Main'):
        """
        Initialises a Blockchain instance.
        
        :param name: str | Used in logs
        :return: None
        """
        super().__init__(name)
        self.block_hashes = []
        self.blocks = {}
        self.corners = {}
        self.unconfirmed_corners = {}

    def new_head(self, block: Block):
        """
        Sets the given block as the new Blockchain head.
        
        :param block: Block
        :return: None
        """
        self.block_hashes.append(block.hash)
        self.blocks.update({block.hash: block})
        self.log(f"New head : [{len(self.blocks)}] - {block.hash.hex()}")

    def get_block_template(self):
        """
        Get a Block instance to be mined based on the current chainstate and pending Corners.
        
        :returns: Block
        """
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


class Guild(Logger):
    """Guild object"""
    def __init__(self, vk=None, sk=None, genesis=None, chain=None, name='Main-Guild'):
        """
        Initialises a Guild instance with a new chain and private key or given ones.
        """
        super().__init__(name)
        if vk is None:
            if sk is None:
                self.sk = SK()
                self.vk = self.sk.vk
            else:
                self.vk = self.sk.vk
        else:
            self.vk = vk
        if chain is None:
            self.chain = BlockChain()
            if genesis is None:
                genesis = Block(self.chain)
            self.chain.new_head(genesis)
        else:
            self.chain = chain
    
    @property
    def raw(self):
        return self.vk.address + self.chain.blocks[self.chain.block_hashes[0]].header


class Wallet(Logger):
    def __init__(self, name='Main-Wallet'):
        super().__init__(name)
        self.addresses = []
        self.corners = []
        self.guilds = []

    def new_address(self):
        address = SK()
        self.addresses.append(address)
        self.debug(f"New address : {address.b58}")
