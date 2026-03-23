import asyncio
import json
import time
from dataclasses import dataclass
from typing import Dict, Set

@dataclass
class Node:
    id: str
    address: str
    last_seen: float
    meta: dict

class SwarmNode:
    def __init__(self, node_id: str, host: str, port: int):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.nodes: Dict[str, Node] = {}
        self.active = False
        self.heartbeat_interval = 5.0
        self.node_timeout = 15.0

    async def start(self):
        self.active = True
        await asyncio.gather(
            self.heartbeat_loop(),
            self.discovery_loop()
        )

    async def stop(self):
        self.active = False

    async def heartbeat_loop(self):
        """Periodically broadcast heartbeat to all known nodes"""
        while self.active:
            self._clean_stale_nodes()
            heartbeat = {
                'type': 'heartbeat',
                'node_id': self.node_id,
                'timestamp': time.time(),
                'meta': {
                    'host': self.host,
                    'port': self.port
                }
            }
            for node in self.nodes.values():
                try:
                    await self._send_message(node.address, heartbeat)
                except Exception as e:
                    print(f'Failed to send heartbeat to {node.id}: {e}')
            await asyncio.sleep(self.heartbeat_interval)

    async def discovery_loop(self):
        """Listen for incoming node discoveries and heartbeats"""
        server = await asyncio.start_server(
            self._handle_connection, 
            self.host, 
            self.port
        )
        async with server:
            await server.serve_forever()

    async def _handle_connection(self, reader, writer):
        """Handle incoming connection and messages"""
        data = await reader.read()
        msg = json.loads(data.decode())

        if msg['type'] == 'heartbeat':
            self._update_node(
                msg['node_id'],
                f"{msg['meta']['host']}:{msg['meta']['port']}",
                msg['timestamp'],
                msg['meta']
            )

        writer.close()
        await writer.wait_closed()

    def _update_node(self, node_id: str, address: str, timestamp: float, meta: dict):
        """Update node information in local registry"""
        if node_id not in self.nodes:
            print(f'Discovered new node: {node_id}')
        self.nodes[node_id] = Node(
            id=node_id,
            address=address,
            last_seen=timestamp,
            meta=meta
        )

    def _clean_stale_nodes(self):
        """Remove nodes that haven't sent a heartbeat recently"""
        current_time = time.time()
        stale_nodes = [
            node_id for node_id, node in self.nodes.items()
            if current_time - node.last_seen > self.node_timeout
        ]
        for node_id in stale_nodes:
            print(f'Node {node_id} timed out, removing')
            del self.nodes[node_id]

    async def _send_message(self, address: str, message: dict):
        """Send message to specific node"""
        host, port = address.split(':')
        port = int(port)
        
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(json.dumps(message).encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()