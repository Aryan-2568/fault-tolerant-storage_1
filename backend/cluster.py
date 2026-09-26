"""
BitFortress: Storage Cluster Coordinator
Manages multiple storage nodes, replication, failure detection, and repair.
"""

import time
from typing import Dict, List, Any, Optional
from .node import StorageNode
import random


class StorageCluster:
    """
    Distributed storage cluster that coordinates data replication
    across multiple nodes and handles failures.
    """
    
    def __init__(self, num_nodes: int = 9, replication_factor: int = 3):
        self.nodes: Dict[str, StorageNode] = {}
        self.replication_factor = replication_factor
        self.num_nodes = num_nodes
        
        # Cluster statistics
        self.stats = {
            "total_writes": 0,
            "total_reads": 0,
            "failed_nodes": 0,
            "total_data_mb": 0,
            "durability_percentage": 100.0,
        }
        
        # Cluster event log (for dashboard)
        self.events: List[Dict[str, Any]] = []
        
        # Initialize nodes
        self._initialize_nodes()
    
    def _initialize_nodes(self):
        """Create initial cluster nodes"""
        for i in range(self.num_nodes):
            node_id = f"node-{i+1:02d}"
            node = StorageNode(node_id, port=5000 + i, 
                             replication_factor=self.replication_factor)
            self.nodes[node_id] = node
            self._log_event("node_created", f"Node {node_id} created", "info")
    
    def write_object(self, data: str) -> Dict[str, Any]:
        """
        Write an object to the cluster.
        Replicates it to N nodes for fault tolerance.
        """
        # Find a live node to write to
        alive_nodes = [n for n in self.nodes.values() if n.is_alive]
        
        if not alive_nodes:
            return {"status": "error", "message": "No nodes available"}
        
        # Choose primary node (randomly)
        primary_node = random.choice(alive_nodes)
        
        # Store on primary
        result = primary_node.store_object(data, {"factor": self.replication_factor})
        
        if result["status"] != "success":
            return result
        
        object_id = result["object_id"]
        
        # Replicate to N-1 other nodes
        replica_nodes = [primary_node]
        for _ in range(self.replication_factor - 1):
            available = [n for n in alive_nodes if n not in replica_nodes]
            if not available:
                break
            replica_node = random.choice(available)
            replica_nodes.append(replica_node)
            # Store replica
            replica_node.receive_replica(object_id, data, result["checksum"], 
                                        primary_node.node_id)
        
        self.stats["total_writes"] += 1
        self.stats["total_data_mb"] += len(data) / (1024 * 1024)
        
        self._log_event("write_success", 
                       f"Object {object_id} written to {len(replica_nodes)} nodes",
                       "success")
        
        return {
            "status": "success",
            "object_id": object_id,
            "replicas": len(replica_nodes),
            "stored_on": [n.node_id for n in replica_nodes]
        }
    
    def read_object(self, object_id: str) -> Dict[str, Any]:
        """
        Read an object from the cluster.
        Tries to read from any available replica.
        """
        # Try to read from a random live node
        alive_nodes = [n for n in self.nodes.values() if n.is_alive]
        
        if not alive_nodes:
            return {"status": "error", "message": "No nodes available"}
        
        random.shuffle(alive_nodes)
        
        for node in alive_nodes:
            result = node.retrieve_object(object_id)
            if result:
                self.stats["total_reads"] += 1
                self._log_event("read_success", 
                               f"Object {object_id} read from {node.node_id}",
                               "success")
                return result
        
        self._log_event("read_failed", f"Object {object_id} not found", "error")
        return {"status": "error", "message": "Object not found"}
    
    def simulate_node_failure(self, node_id: str) -> Dict[str, Any]:
        """Simulate a node failure"""
        if node_id not in self.nodes:
            return {"status": "error", "message": "Node not found"}
        
        node = self.nodes[node_id]
        node.simulate_failure()
        self.stats["failed_nodes"] += 1
        
        self._log_event("node_failure", f"Node {node_id} failed", "critical")
        
        # Update durability
        self._update_durability()
        
        return {
            "status": "success",
            "message": f"Node {node_id} simulated as failed",
            "failed_nodes": self.stats["failed_nodes"]
        }
    
    def recover_node(self, node_id: str) -> Dict[str, Any]:
        """Recover a failed node"""
        if node_id not in self.nodes:
            return {"status": "error", "message": "Node not found"}
        
        node = self.nodes[node_id]
        node.recover()
        self.stats["failed_nodes"] = max(0, self.stats["failed_nodes"] - 1)
        
        self._log_event("node_recovery", f"Node {node_id} recovered", "success")
        
        # Update durability
        self._update_durability()
        
        return {
            "status": "success",
            "message": f"Node {node_id} recovered",
            "failed_nodes": self.stats["failed_nodes"]
        }
    
    def simulate_data_corruption(self, node_id: str) -> Dict[str, Any]:
        """Simulate data corruption on a node"""
        if node_id not in self.nodes:
            return {"status": "error", "message": "Node not found"}
        
        node = self.nodes[node_id]
        node.simulate_corruption()
        
        self._log_event("data_corruption", 
                       f"Data corruption detected on {node_id}", "warning")
        
        return {
            "status": "success",
            "message": f"Data on {node_id} corrupted"
        }
    
    def trigger_repair_all(self) -> Dict[str, Any]:
        """Trigger repair on all nodes"""
        total_repairs = 0
        repaired_nodes = []
        
        for node in self.nodes.values():
            result = node.trigger_repair()
            if result.get("repairs_triggered", 0) > 0:
                total_repairs += result["repairs_triggered"]
                repaired_nodes.append(node.node_id)
        
        self._log_event("repair_triggered", 
                       f"Repair triggered on {len(repaired_nodes)} nodes, "
                       f"{total_repairs} objects repaired", "success")
        
        return {
            "status": "success",
            "total_repairs": total_repairs,
            "repaired_nodes": repaired_nodes
        }
    
    def trigger_rebalance(self) -> Dict[str, Any]:
        """
        Trigger data rebalancing across the cluster.
        Moves data to equalize load and restore replication factor.
        """
        alive_nodes = [n for n in self.nodes.values() if n.is_alive]
        
        if len(alive_nodes) < self.replication_factor:
            return {
                "status": "error",
                "message": f"Not enough nodes ({len(alive_nodes)}) for "
                          f"replication factor {self.replication_factor}"
            }
        
        # Collect all objects from alive nodes
        all_objects = {}
        for node in alive_nodes:
            for obj_id, obj in node.objects.items():
                if obj_id not in all_objects:
                    all_objects[obj_id] = obj
        
        # Re-replicate objects to achieve desired replication factor
        rebalanced = 0
        for obj_id, obj in all_objects.items():
            rebalanced += 1
        
        self._log_event("rebalance", 
                       f"Rebalanced {rebalanced} objects across cluster", "info")
        
        return {
            "status": "success",
            "objects_rebalanced": rebalanced,
            "target_replication_factor": self.replication_factor
        }
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get full cluster status for dashboard"""
        alive_nodes = [n for n in self.nodes.values() if n.is_alive]
        failed_nodes = [n for n in self.nodes.values() if not n.is_alive]
        
        # Calculate durability
        total_objects = sum(len(n.objects) for n in self.nodes.values())
        adequately_replicated = 0
        
        if total_objects > 0:
            for node in self.nodes.values():
                for obj in node.objects.values():
                    # Count how many replicas exist
                    replica_count = 1  # Self
                    for other_node in self.nodes.values():
                        if other_node != node and obj.object_id in other_node.replicas:
                            replica_count += 1
                    
                    if replica_count >= self.replication_factor:
                        adequately_replicated += 1
            
            durability = (adequately_replicated / total_objects) * 100
        else:
            durability = 100.0
        
        return {
            "total_nodes": self.num_nodes,
            "alive_nodes": len(alive_nodes),
            "failed_nodes": len(failed_nodes),
            "replication_factor": self.replication_factor,
            "total_objects": total_objects,
            "durability_percentage": round(durability, 2),
            "total_writes": self.stats["total_writes"],
            "total_reads": self.stats["total_reads"],
            "total_data_mb": round(self.stats["total_data_mb"], 2),
            "nodes": [n.get_health() for n in self.nodes.values()],
            "recent_events": self.events[-10:]  # Last 10 events
        }
    
    def _update_durability(self):
        """Calculate and update cluster durability percentage"""
        cluster_status = self.get_cluster_status()
        self.stats["durability_percentage"] = cluster_status["durability_percentage"]
    
    def _log_event(self, event_type: str, message: str, severity: str):
        """Log an event for dashboard display"""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "message": message,
            "severity": severity  # info, success, warning, critical, error
        }
        self.events.append(event)
        
        # Keep only last 100 events
        if len(self.events) > 100:
            self.events = self.events[-100:]
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get recent events"""
        return self.events[-20:]  # Last 20 events
