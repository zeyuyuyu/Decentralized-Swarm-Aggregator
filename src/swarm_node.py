import asyncio
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp

@dataclass
class NodeInfo:
    id: str
    address: str
    last_seen: datetime
    capabilities: List[str]

class SwarmNode:
    def __init__(self, node_id: str, host: str, port: int):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.peers: Dict[str, NodeInfo] = {}
        self.capabilities = ['compute', 'storage']
        self.is_running = False

    async def start(self):
        self.is_running = True
        await asyncio.gather(
            self.discovery_heartbeat(),
            self.maintain_mesh()
        )

    async def discovery_heartbeat(self):
        """Broadcast node presence and discover peers"""
        while self.is_running:
            try:
                async with aiohttp.ClientSession() as session:
                    # Broadcast presence to known peers
                    for peer in self.peers.values():
                        url = f'http://{peer.address}/heartbeat'
                        payload = {
                            'node_id': self.node_id,
                            'address': f'{self.host}:{self.port}',
                            'capabilities': self.capabilities,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        try:
                            async with session.post(url, json=payload) as resp:
                                if resp.status == 200:
                                    peer_data = await resp.json()
                                    self._update_peer_info(peer_data)
                        except Exception as e:
                            print(f'Error connecting to peer {peer.address}: {e}')
                            
            except Exception as e:
                print(f'Discovery heartbeat error: {e}')
            await asyncio.sleep(30)

    async def maintain_mesh(self):
        """Clean up stale peers and maintain mesh network"""
        while self.is_running:
            now = datetime.utcnow()
            # Remove peers not seen in last 90 seconds
            stale_peers = [
                pid for pid, peer in self.peers.items()
                if (now - peer.last_seen).total_seconds() > 90
            ]
            for pid in stale_peers:
                del self.peers[pid]
            
            await asyncio.sleep(30)

    def _update_peer_info(self, peer_data: dict):
        """Update peer information from heartbeat data"""
        pid = peer_data['node_id']
        self.peers[pid] = NodeInfo(
            id=pid,
            address=peer_data['address'],
            last_seen=datetime.utcnow(),
            capabilities=peer_data['capabilities']
        )

    async def stop(self):
        """Gracefully shutdown node"""
        self.is_running = False

    async def get_network_status(self) -> dict:
        """Get current network mesh status"""
        return {
            'node_id': self.node_id,
            'address': f'{self.host}:{self.port}',
            'peers': len(self.peers),
            'capabilities': self.capabilities,
            'connected_peers': [
                {
                    'id': p.id,
                    'address': p.address,
                    'capabilities': p.capabilities
                } for p in self.peers.values()
            ]
        }