"""
BitFortress: Distributed Storage Node
Each node stores data and communicates with other nodes for replication and repair.
"""

import json
import hashlib
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import random

@dataclass
class StoredObject:
    """Represents a stored object with metadata"""
    object_id: str
    data: str
    timestamp: float
    checksum: str
    replica_locations: List[str]  # Node IDs where this is replicated
    version: int = 1
    
    def to_dict(self):
        return asdict(self)


class StorageNode:
    """
    A single storage node in the distributed system.
    - Stores objects locally
    - Replicates data to other nodes
    - Detects failures and triggers repairs
    """
    
    def __init__(self, node_id: str, port: int, replication_factor: int = 3):
        self.node_id = node_id
        self.port = port
        self.replication_factor = replication_factor
        
        # Local storage
        self.objects: Dict[str, StoredObject] = {}
        
        # Node health tracking
        self.is_alive = True
        self.last_heartbeat = time.time()
        self.failed_at = None
        
        # Statistics for dashboard
        self.stats = {
            "total_objects": 0,
            "total_replicas": 0,
            "failed_replicas": 0,
            "repair_operations": 0,
            "storage_used_mb": 0,
        }
        
        # Track replicas stored on this node (from other nodes)
        self.replicas: Dict[str, List[str]] = {}  # object_id -> [data_chunks]
        
    def store_object(self, data: str, replication_config: Dict) -> Dict[str, Any]:
        """
        Store an object and replicate it to other nodes.
        Returns metadata about where it's stored.
        """
        if not self.is_alive:
            return {"status": "error", "message": "Node is dead"}
        
        object_id = str(uuid.uuid4())[:8]
        checksum = self._calculate_checksum(data)
        
        # Create storage object
        obj = StoredObject(
            object_id=object_id,
            data=data,
            timestamp=time.time(),
            checksum=checksum,
            replica_locations=[self.node_id],  # Self is first replica
            version=1
        )
        
        # Store locally
        self.objects[object_id] = obj
        
        # Update stats
        self.stats["total_objects"] += 1
        self.stats["total_replicas"] += 1
        self.stats["storage_used_mb"] += len(data) / (1024 * 1024)
        
        return {
            "status": "success",
            "object_id": object_id,
            "checksum": checksum,
            "stored_on_node": self.node_id,
            "replication_factor": self.replication_factor
        }
    
    def retrieve_object(self, object_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an object from this node"""
        if not self.is_alive:
            return None
        
        if object_id in self.objects:
            obj = self.objects[object_id]
            return {
                "object_id": object_id,
                "data": obj.data,
                "checksum": obj.checksum,
                "retrieved_from": self.node_id,
                "checksum_valid": obj.checksum == self._calculate_checksum(obj.data)
            }
        return None
    
    def receive_replica(self, object_id: str, data: str, checksum: str, source_node: str):
        """Store a replica received from another node"""
        if not self.is_alive:
            return False
        
        # Verify checksum
        if checksum != self._calculate_checksum(data):
            # Corruption detected!
            return False
        
        if object_id not in self.replicas:
            self.replicas[object_id] = []
        
        self.replicas[object_id].append(data)
        self.stats["total_replicas"] += 1
        return True
    
    def simulate_failure(self):
        """Simulate this node failing"""
        self.is_alive = False
        self.failed_at = time.time()
        self.stats["storage_used_mb"] = 0  # Data inaccessible
    
    def recover(self):
        """Recover this node from failure"""
        self.is_alive = True
        self.last_heartbeat = time.time()
        self.failed_at = None
        # Recalculate storage
        self.stats["storage_used_mb"] = sum(
            len(obj.data) / (1024 * 1024) for obj in self.objects.values()
        )
    
    def simulate_corruption(self):
        """Simulate data corruption on this node"""
        if self.objects:
            random_obj_id = random.choice(list(self.objects.keys()))
            obj = self.objects[random_obj_id]
            # Corrupt the data
            obj.data = obj.data[:-10] + "CORRUPTED!"
            self.stats["failed_replicas"] += 1
    
    def trigger_repair(self) -> Dict[str, Any]:
        """Check for corrupted data and repair"""
        if not self.is_alive:
            return {"status": "node_dead"}
        
        repairs = 0
        for obj_id, obj in list(self.objects.items()):
            # Verify integrity
            if obj.checksum != self._calculate_checksum(obj.data):
                # Corruption detected - would be repaired from replicas
                repairs += 1
                # Simulate repair
                obj.version += 1
        
        self.stats["repair_operations"] += repairs
        return {
            "node_id": self.node_id,
            "repairs_triggered": repairs,
            "status": "success"
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Get health status of this node"""
        uptime = 0
        if self.is_alive:
            uptime = time.time() - self.last_heartbeat
        elif self.failed_at:
            uptime = time.time() - self.failed_at
        
        return {
            "node_id": self.node_id,
            "is_alive": self.is_alive,
            "port": self.port,
            "objects_stored": len(self.objects),
            "total_replicas": self.stats["total_replicas"],
            "failed_replicas": self.stats["failed_replicas"],
            "storage_used_mb": round(self.stats["storage_used_mb"], 2),
            "uptime_seconds": round(uptime, 2),
            "repair_operations": self.stats["repair_operations"],
            "checksum_mismatches": self._count_checksum_mismatches()
        }
    
    def _count_checksum_mismatches(self) -> int:
        """Count how many objects have invalid checksums"""
        count = 0
        for obj in self.objects.values():
            if obj.checksum != self._calculate_checksum(obj.data):
                count += 1
        return count
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate SHA256 checksum of data"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get_replicas_info(self) -> Dict[str, Any]:
        """Get information about replicas stored on this node"""
        return {
            "node_id": self.node_id,
            "replica_count": len(self.replicas),
            "total_replica_data_mb": sum(
                sum(len(chunk) for chunk in chunks) / (1024 * 1024)
                for chunks in self.replicas.values()
            )
        }
