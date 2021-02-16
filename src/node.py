import asyncio
import blockchain
from log import Logger
import time


class Node(Logger):
    def __init__(self, name='Node'):
        super().__init__(name)
        self.connect = ['192.168.0.12:8888']
        self.peers = {}
        self.last_id = 0
        self.server = None

    def run(self):
        asyncio.run(self.main())

    async def main(self):
        for ip in self.connect:
            try:
                await self.outbound(ip)
            except ConnectionRefusedError:
                self.warning(f"Connection refused : {ip}")
        self.log("Node is starting..")
        self.server = await asyncio.start_server(self.inbound, '0.0.0.0', 8888)
        addr = self.server.sockets[0].getsockname()
        self.log(f"Listening on {addr}")
        async with self.server:
            await self.server.serve_forever()

    async def inbound(self, reader, writer):
        await Peer(reader, writer, self).in_handler()

    async def outbound(self, arg1, arg2=None):
        if arg2 is not None:
            ip, port = arg1, arg2
        else:
            ip, port = arg1.split(":")
        asyncio.ensure_future(Peer(*(await asyncio.open_connection(ip, port)), self).in_handler())


class Peer(Logger):
    CHUNK_SIZE = 1024
    version = 0
    BPM = 20
    TIMEOUT = 5
    p_flags = {0: "hello",
               1: "ping",
               2: "pong",
               3: "heartbeat"}
    ver = version.to_bytes(1, 'big')

    def __init__(self, reader, writer, node):
        self.ip, self.port = writer.get_extra_info('peername')
        super().__init__(f"{self.ip}:{self.port}")
        self.log("Connected.")
        self.connected = True
        asyncio.ensure_future(self.heartbeat_core())
        self.reader = reader
        self.writer = writer
        self.node = node
        self.id = self.node.last_id = self.node.last_id + 1
        self.node.peers.update({self.id: self})
        self.last_ping_id = 0
        self.last_ping_duration = 0
        self.pings = {}

    async def in_handler(self):
        try:
            await self.hello()
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
        finally:
            self.log("Connection closed.")
            if self.id in self.node.peers:
                del self.node.peers[self.id]
            self.writer.close()
            self.connected = False

    async def send(self, data):
        data = self.version.to_bytes(2, 'big') + data
        chunks = [data[i:i + self.CHUNK_SIZE] for i in range(0, len(data) - self.CHUNK_SIZE, self.CHUNK_SIZE)] + [
            data[len(data) - self.CHUNK_SIZE:]]
        self.debug(chunks)
        for chunk in chunks[:-1]:
            self.writer.write(b'\xff\xff' + chunk)
            self.debug(b'\xff\xff' + chunk)
            await self.writer.drain()
        self.writer.write(len(chunks[-1]).to_bytes(2, 'big') + chunks[-1])
        self.debug(len(chunks[-1]).to_bytes(2, 'big') + chunks[-1])
        await self.writer.drain()

    async def parse(self, data):
        version = int.from_bytes(data[:2], 'big')
        if version != self.version:
            self.error(f"Version is not the same : {version} and not {self.version}. Closing connection.")
            await self.send(b"Incorrect version !")
            self.writer.close()
            del self.node.peers[self.id]
            return
        p_flag = int.from_bytes(data[2:4], 'big')
        if p_flag in self.p_flags:
            await getattr(self, 'parse_' + self.p_flags[p_flag])(data[3:])
        else:
            self.error(f"Unknown payload Flag {p_flag}. Closing connection.")
            await self.send(b'Unknown Flag !')
            del self.node.peers[self.id]
            return

    async def parse_hello(self, data):
        self.debug("Hello")

    async def hello(self):
        await self.send(self.version.to_bytes(2, 'big') + b'\x00\x00')
        self.debug("Sent Hello.")

    async def ping(self):
        self.last_ping_id += 1
        await self.send((1).to_bytes(2, 'big') + self.last_ping_id.to_bytes(2, 'big'))
        self.pings.update({self.last_ping_id: time.time()})
        self.debug("ping")

    async def pong(self, id):
        await self.send((2).to_bytes(2, 'big') + id.to_bytes(2, 'big'))

    async def parse_ping(self, data):
        await self.pong(int.from_bytes(data, 'big'))
        self.debug("pong")

    async def parse_pong(self, data):
        duration = time.time() - self.pings.pop(int.from_bytes(data, 'big'))
        self.debug(f"Ping duration : {duration}")
        self.last_ping_duration = duration

    def disconnect(self):
        self.writer.close()

    async def heartbeat_core(self):
        while self.connected:
            await asyncio.sleep(60/self.BPM)
            await self.heartbeat()
            await self.ping()
            self.log(f"Last ping duration : {self.last_ping_duration} s")

    async def heartbeat(self):
        await self.send((3).to_bytes(2, 'big'))

    async def parse_heartbeat(self, data):
        self.debug("poum poum.")


if __name__ == '__main__':
    node = Node()
    node.run()