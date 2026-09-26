"""
BitFortress: FastAPI Backend Server
Serves the distributed storage cluster and provides HTTP APIs for the frontend dashboard.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from backend.cluster import StorageCluster

# Initialize FastAPI app
app = FastAPI(
    title="BitFortress - Distributed Storage",
    description="Fault-tolerant distributed object storage with real-time monitoring"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage cluster (9 nodes, 3x replication)
cluster = StorageCluster(num_nodes=9, replication_factor=3)

# ============= Pydantic Models =============

class WriteRequest(BaseModel):
    data: str
    description: Optional[str] = None


class NodeActionRequest(BaseModel):
    node_id: str
    action: str  # "fail", "recover", "corrupt"


# ============= Storage APIs =============

@app.post("/api/write")
def write_object(request: WriteRequest):
    """
    Write an object to the distributed storage system.
    Data will be replicated across multiple nodes.
    """
    result = cluster.write_object(request.data)
    if result["status"] == "success":
        return {
            "success": True,
            "object_id": result["object_id"],
            "replicas": result["replicas"],
            "stored_on_nodes": result["stored_on"],
            "description": request.description
        }
    else:
        raise HTTPException(status_code=500, detail=result.get("message", "Write failed"))


@app.get("/api/read/{object_id}")
def read_object(object_id: str):
    """
    Read an object from the distributed storage system.
    Retrieves from the first available replica.
    """
    result = cluster.read_object(object_id)
    if result["status"] == "success":
        return {
            "success": True,
            "object_id": object_id,
            "data": result["data"],
            "retrieved_from": result["retrieved_from"],
            "checksum_valid": result["checksum_valid"]
        }
    else:
        raise HTTPException(status_code=404, detail="Object not found")


# ============= Cluster Management APIs =============

@app.get("/api/cluster/status")
def get_cluster_status():
    """Get full cluster status and metrics"""
    return cluster.get_cluster_status()


@app.post("/api/cluster/node/fail")
def fail_node(request: NodeActionRequest):
    """Simulate a node failure"""
    result = cluster.simulate_node_failure(request.node_id)
    if result["status"] == "success":
        return {"success": True, "message": result["message"]}
    else:
        raise HTTPException(status_code=404, detail=result.get("message"))


@app.post("/api/cluster/node/recover")
def recover_node(request: NodeActionRequest):
    """Recover a failed node"""
    result = cluster.recover_node(request.node_id)
    if result["status"] == "success":
        return {"success": True, "message": result["message"]}
    else:
        raise HTTPException(status_code=404, detail=result.get("message"))


@app.post("/api/cluster/node/corrupt")
def corrupt_node(request: NodeActionRequest):
    """Simulate data corruption on a node"""
    result = cluster.simulate_data_corruption(request.node_id)
    if result["status"] == "success":
        return {"success": True, "message": result["message"]}
    else:
        raise HTTPException(status_code=404, detail=result.get("message"))


@app.post("/api/cluster/repair")
def trigger_repair():
    """Trigger repair operation on all nodes"""
    result = cluster.trigger_repair_all()
    return {
        "success": True,
        "total_repairs": result["total_repairs"],
        "repaired_nodes": result["repaired_nodes"]
    }


@app.post("/api/cluster/rebalance")
def trigger_rebalance():
    """Trigger data rebalancing across the cluster"""
    result = cluster.trigger_rebalance()
    if result["status"] == "success":
        return {
            "success": True,
            "objects_rebalanced": result["objects_rebalanced"]
        }
    else:
        raise HTTPException(status_code=500, detail=result.get("message"))


@app.get("/api/cluster/events")
def get_events():
    """Get recent cluster events"""
    return {"events": cluster.get_events()}


@app.post("/api/demo/stress-test")
def stress_test_demo():
    """
    Run a demo stress test:
    1. Write some data
    2. Fail a few nodes
    3. Show recovery
    """
    events_log = []
    
    # Write multiple objects
    for i in range(5):
        data = f"Demo data object {i+1}: " + "x" * 1000
        result = cluster.write_object(data)
        if result["status"] == "success":
            events_log.append(f"✓ Written object {result['object_id']}")
    
    # Fail some nodes
    import random
    nodes_to_fail = random.sample(list(cluster.nodes.keys()), 2)
    for node_id in nodes_to_fail:
        cluster.simulate_node_failure(node_id)
        events_log.append(f"✗ Node {node_id} failed")
    
    # Trigger repair
    repair_result = cluster.trigger_repair_all()
    events_log.append(f"↻ Repair triggered: {repair_result['total_repairs']} objects repaired")
    
    # Recover nodes
    for node_id in nodes_to_fail:
        cluster.recover_node(node_id)
        events_log.append(f"✓ Node {node_id} recovered")
    
    return {
        "success": True,
        "events": events_log,
        "cluster_status": cluster.get_cluster_status()
    }


# ============= Health Check =============

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "BitFortress"}


@app.get("/")
def root():
    """Root endpoint - redirects to dashboard"""
    return {
        "service": "BitFortress - Distributed Storage System",
        "status": "running",
        "api_docs": "/docs",
        "dashboard": "http://localhost:3000"
    }


if __name__ == "__main__":
    print("""
    
    ╔═══════════════════════════════════════════════════════════╗
    ║           BitFortress - Storage Cluster                   ║
    ║   Distributed Object Storage with Fault Tolerance         ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Backend API running on http://localhost:8000
    📊 Interactive docs on http://localhost:8000/docs
    🎨 Frontend dashboard: http://localhost:3000
    
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
