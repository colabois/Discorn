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

    async def handle_connections(self, reader, writer):
        pass


if __name__ == '__main__':
    node = Node()
    node.run()
