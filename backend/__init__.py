"""
BitFortress: Distributed Object Storage System
Fault-tolerant storage with automatic replication and repair capabilities.
"""

from .node import StorageNode
from .cluster import StorageCluster

__all__ = ['StorageNode', 'StorageCluster']
__version__ = '1.0.0'
