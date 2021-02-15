import asyncio
import blockchain
from log import Logger


class Node(Logger):
    def __init__(self, name='Node'):
        super().__init__(name)
        self.peers = []

    def run(self):
        asyncio.run(self.main())

    async def main(self):
        self.log("Node is starting..")
        self.server = await asyncio.start_server(self.inbound, '0.0.0.0', 8888)
        addr = self.server.sockets[0].getsockname()
        self.log(f"Listening on {addr}")
        async with self.server:
            await self.server.serve_forever()

    async def inbound(self, reader, writer):
        p = Peer(reader, writer, node)
        await p.in_handler()

class Peer(Logger):
    CHUNK_SIZE = 1024
    def __init__(self, reader, writer, node):
        super().__init__(writer.get_extra_info)
        self.log("Connected.")
        self.reader = reader
        self.writer = writer
        self.node = node
    
    async def in_handler(self):
        while True:
            magic = await self.reader.read(1)
            data = b''
            while magic == b'\x00':
                data += await self.reader.read(self.CHUNK_SIZE)
                magic = await self.reader.read(1)
            data += await self.reader.read(int.from_bytes(magic, 'big'))
            

if __name__ == '__main__':
    node = Node()
    node.run()
