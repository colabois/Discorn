import asyncio
import blockchain
from log import Logger


class Node(Logger):
    def __init__(self, name='Node'):
        super().__init__(name)
        self.peers = {}
        self.last_id = 0

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
    version = 0
    p_flags = {0:"hello",
               }
    ver = version.to_bytes(1, 'big')
    def __init__(self, reader, writer, node):
        self.ip, self.port = writer.get_extra_info('peername')
        super().__init__(f"{self.ip}:{self.port}")
        self.log("Connected.")
        self.reader = reader
        self.writer = writer
        self.node = node
        self.id = self.node.last_id = self.node.last_id + 1
        self.node.peers.update({self.id: self})
    
    async def in_handler(self):
        self.send()
        while True:
            magic = await self.reader.read(2)
            data = b''
            while magic == b'\xff\xff':
                data += await self.reader.read(self.CHUNK_SIZE)
                magic = await self.reader.read(2)
            data += await self.reader.read(int.from_bytes(magic, 'big'))
            if magic == b'':
                break
            await self.parse(data)
        self.log("Connection closed.")
        if self.id in self.node.peers:
            del self.node.peers[self.id]
        self.writer.close()

    async def send(self, data):
        chunks = [data[i:i+self.CHUNK_SIZE] for i in range(0,len(data) - self.CHUNK_SIZE, self.CHUNK_SIZE)] + [data[len(data) - self.CHUNK_SIZE:]]
        self.debug(chunks)
        for chunk in chunks[:-1]:
            self.writer.write(b'\xff\xff'+ chunk)
            self.debug(b'\xff\xff'+ chunk)
            await self.writer.drain()
        self.writer.write(len(chunks[-1]).to_bytes(2, 'big') + chunks[-1])
        self.debug(len(chunks[-1]).to_bytes(2, 'big') + chunks[-1])
        await self.writer.drain()
        
    
    async def parse(self, data):
        version = int.from_bytes(data[:1], 'big')
        if version != self.version:
            self.error(f"Version is not the same : {version} and not {self.version}. Closing connection.")
            await self.send(b"Incorrect version !")
            self.writer.close()
            del self.node.peers[self.id]
            return
        p_flag = int.from_bytes(data[1:3], 'big')
        if p_flag in self.p_flags:
            await getattr(self, 'parse_'+self.p_flags[p_flag])(data[3:])
        else:
            self.error(f"Unknown payload Flag {p_flag}. Closing connection.")
            await self.send(b'Unknown Flag !')
            del self.node.peers[self.id]
            return
    
    async def parse_hello(self, data):
        self.debug("Hello")


if __name__ == '__main__':
    node = Node()
    node.run()
