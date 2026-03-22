import os
import time
import random
from typing import List, Dict

class SwarmNode:
    def __init__(self, node_id: str, connections: List[str]):
        self.node_id = node_id
        self.connections = connections
        self.data = {}

    def update_data(self, new_data: Dict[str, any]):
        self.data.update(new_data)

class SwarmAggregator:
    def __init__(self, node_ids: List[str]):
        self.nodes = [SwarmNode(node_id, []) for node_id in node_ids]
        self.node_map = {node.node_id: node for node in self.nodes}

    def connect_nodes(self):
        for node in self.nodes:
            node.connections = random.sample([n.node_id for n in self.nodes if n.node_id != node.node_id], k=3)

    def aggregate_data(self):
        for node in self.nodes:
            for conn_id in node.connections:
                conn_node = self.node_map[conn_id]
                node.update_data(conn_node.data)

    def run(self):
        self.connect_nodes()
        while True:
            for node in self.nodes:
                node.update_data({
                    f'sensor_{i}': random.uniform(0, 100)
                    for i in range(5)
                })
            self.aggregate_data()
            time.sleep(5)

if __name__ == '__main__':
    agg = SwarmAggregator(['node1', 'node2', 'node3', 'node4', 'node5'])
    agg.run()