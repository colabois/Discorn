import asyncio
import blockchain
from log import Logger
import time
import collections


class Node(Logger):
    def __init__(self, name='Node'):
        super().__init__(name)
        self.connect = ['192.168.0.12:8888', '192.168.0.14:8888']
        self.peers = {}
        self.guilds = {}
        self.last_id = 0
        self.server = None
        self.serve = True

    def run(self):
        asyncio.run(self.main())

    async def main(self):
        self.log("Node is starting..")
        for ip in self.connect:
            try:
                await self.outbound(ip)
            except ConnectionRefusedError:
                self.warning(f"Connection refused : {ip}")
        if self.serve:
            asyncio.ensure_future(self.listen())

        #Main Loop
        while True:
            await asyncio.sleep(60)

    async def listen(self):
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
    BPM = 50
    TIMEOUT = 20
    p_flags = {0: "hello",
               1: "ping",
               2: "pong",
               3: "heartbeat",
               4: "getguilds",
               5: "newguild",
               6: "disconnecting",
               7: "getchainstatus",
               8: "sendchainstatus"}
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
        self.last_heartbeat = time.time()
        self.guilds = {}

    async def in_handler(self):
        try:
            await self.hello()
            await self.getguilds()
            while self.connected:
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
            self.disconnect()

    async def send(self, data):
        if self.connected:
            data = self.version.to_bytes(2, 'big') + data
            chunks = [data[i:i + self.CHUNK_SIZE] for i in range(0, len(data) - self.CHUNK_SIZE, self.CHUNK_SIZE)] + [
                data[len(data) - self.CHUNK_SIZE:]]
            for chunk in chunks[:-1]:
                self.writer.write(b'\xff\xff' + chunk)
                await self.writer.drain()
            self.writer.write(len(chunks[-1]).to_bytes(2, 'big') + chunks[-1])
            await self.writer.drain()

    async def parse(self, data):
        version = int.from_bytes(data[:2], 'big')
        if version != self.version:
            self.error(f"Version is not the same : {version} and not {self.version}. Closing connection.")
            await self.disconnecting(b"Incorrect version !")
            return self.disconnect()
        p_flag = int.from_bytes(data[2:4], 'big')
        if p_flag in self.p_flags:
            await getattr(self, 'parse_' + self.p_flags[p_flag])(data[4:])
        else:
            self.error(f"Unknown payload Flag {p_flag}. Closing connection.")
            await self.disconnecting(b'Unknown Flag !')
            self.disconnect()
            return

    async def parse_hello(self, data):
        self.debug("Hello")

    async def hello(self):
        await self.send(self.version.to_bytes(2, 'big') + b'\x00\x00')

    async def ping(self):
        self.last_ping_id = self.last_ping_id + 1 if self.last_ping_id <= 65535 else 0
        await self.send((1).to_bytes(2, 'big') + self.last_ping_id.to_bytes(2, 'big'))
        self.pings.update({self.last_ping_id: time.time()})

    async def pong(self, id):
        await self.send((2).to_bytes(2, 'big') + id.to_bytes(2, 'big'))

    async def parse_ping(self, data):
        await self.pong(int.from_bytes(data, 'big'))

    async def parse_pong(self, data):
        duration = time.time() - self.pings.pop(int.from_bytes(data, 'big'))
        self.last_ping_duration = duration

    def disconnect(self):
        if self.connected:
            del self.node.peers[self.id]
            self.writer.close()
            self.connected = False
            self.log("Connection closed.")

    async def heartbeat_core(self):
        while self.connected:
            await asyncio.sleep(60/self.BPM)
            await self.heartbeat()
            await self.ping()
            if time.time() - self.last_heartbeat > (60/self.BPM) * self.TIMEOUT:
                self.warning("Timeout. Disconnecting.")
                self.disconnect()

    async def heartbeat(self):
        await self.send((3).to_bytes(2, 'big'))

    async def parse_heartbeat(self, data):
        self.last_heartbeat = time.time()
    
    async def getguilds(self):
        await self.send((4).to_bytes(2, 'big'))
    
    async def parse_getguilds(self, data):
        for _, guild in self.node.guilds.items():
            await self.newguild(guild)
    
    async def newguild(self, guild):
        await self.send((5).to_bytes(2, 'big') + guild.raw)
    
    async def parse_newguild(self, data):
        self.guilds.update({data: None})
        await self.getchainstatus(data)
    
    async def disconnecting(self, mess):
        await self.send((6).to_bytes(2, 'big') + mess)
    
    async def parse_disconnecting(self, data):
        self.error(f"Remote closing connection : {data.decode('utf-8')}. Disconnecting.")
        self.disconnect()

    async def getchainstatus(self, guild):
        data = guild.raw if guild is blockchain.Guild else guild
        await self.send((7).to_bytes(2, 'big') + data)

    async def parse_getchainstatus(self, data):
        if data not in self.node.guilds:
            self.error("Guild Unknown, disconnecting...")
            await self.disconnecting("Guild Unknown.")
            self.disconnect()
        else:
            await self.sendchainstatus(self.node.guilds[data])

    async def sendchainstatus(self, guild):
        data = (8).to_bytes(2, 'big')
        data += guild.raw
        data += len(guild.chain.block_hashes).to_bytes(4, 'big')  # Block Height
        data += len([peer for peer in self.node.peers.values() if guild.raw in peer.guilds]).to_bytes(2, 'big')  # Peercount
        await self.send(data)

    async def parse_sendchainstatus(self, data):
        self.guilds[self.guilds[data[:109]]] = {'height': int.from_bytes(data[109:109+4], 'big'),
                                                'peercount': int.from_bytes(data[109+4:])}
        self.log(self.guilds)


if __name__ == '__main__':
    node = Node()
    g = blockchain.Guild()
    node.guilds.update({g.raw:g})
    node.run()
