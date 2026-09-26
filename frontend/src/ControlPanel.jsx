import React, { useState } from 'react';
import './ControlPanel.css';

function ControlPanel({ API_BASE }) {
  const [selectedNode, setSelectedNode] = useState('node-01');
  const [writeData, setWriteData] = useState('Sample data for testing');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const showMessage = (msg, duration = 3000) => {
    setMessage(msg);
    setTimeout(() => setMessage(''), duration);
  };

  const handleAction = async (action, endpoint, body = {}) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      
      if (response.ok) {
        const data = await response.json();
        showMessage(`✓ ${action} successful`);
      } else {
        showMessage(`✗ ${action} failed`, 2000);
      }
    } catch (error) {
      showMessage(`✗ Error: ${error.message}`, 2000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="control-panel">
      <h2>⚙️ Control Panel</h2>

      {/* Storage Operations */}
      <div className="control-section">
        <h3>💾 Storage Operations</h3>
        
        <div className="control-group">
          <label>Write Data to Cluster:</label>
          <textarea
            value={writeData}
            onChange={(e) => setWriteData(e.target.value)}
            placeholder="Enter data to write..."
            rows="3"
            disabled={loading}
          />
          <button
            className="btn btn-primary"
            onClick={() => handleAction('Write', '/write', { data: writeData, description: 'Demo write' })}
            disabled={loading}
          >
            ✍️ Write Object
          </button>
        </div>
      </div>

      {/* Node Operations */}
      <div className="control-section">
        <h3>🔧 Node Operations</h3>
        
        <div className="control-group">
          <label>Select Node:</label>
          <select
            value={selectedNode}
            onChange={(e) => setSelectedNode(e.target.value)}
            disabled={loading}
          >
            {Array.from({ length: 9 }, (_, i) => `node-${String(i + 1).padStart(2, '0')}`).map(
              (nodeId) => (
                <option key={nodeId} value={nodeId}>
                  {nodeId}
                </option>
              )
            )}
          </select>
        </div>

        <div className="button-group">
          <button
            className="btn btn-danger"
            onClick={() => handleAction('Fail Node', '/cluster/node/fail', { node_id: selectedNode })}
            disabled={loading}
          >
            🔴 Fail Node
          </button>
          <button
            className="btn btn-success"
            onClick={() => handleAction('Recover Node', '/cluster/node/recover', { node_id: selectedNode })}
            disabled={loading}
          >
            🟢 Recover Node
          </button>
          <button
            className="btn btn-warning"
            onClick={() => handleAction('Corrupt Data', '/cluster/node/corrupt', { node_id: selectedNode })}
            disabled={loading}
          >
            ⚠️ Corrupt Data
          </button>
        </div>
      </div>

      {/* Cluster Operations */}
      <div className="control-section">
        <h3>🏰 Cluster Operations</h3>
        
        <div className="button-group">
          <button
            className="btn btn-info"
            onClick={() => handleAction('Repair', '/cluster/repair')}
            disabled={loading}
          >
            ↻ Trigger Repair
          </button>
          <button
            className="btn btn-info"
            onClick={() => handleAction('Rebalance', '/cluster/rebalance')}
            disabled={loading}
          >
            ⚖️ Rebalance Data
          </button>
        </div>
      </div>

      {/* Demo Scenarios */}
      <div className="control-section">
        <h3>🎬 Demo Scenarios</h3>
        
        <button
          className="btn btn-demo"
          onClick={() => handleAction('Demo', '/demo/stress-test')}
          disabled={loading}
        >
          🚀 Run Stress Test Demo
        </button>
        
        <p className="scenario-description">
          Automatically writes data, fails nodes, and triggers repairs. Perfect for showing judges the system in action!
        </p>
      </div>

      {/* Status Message */}
      {message && (
        <div className={`status-message ${message.includes('✓') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Processing...</p>
        </div>
      )}

      {/* Quick Tips */}
      <div className="tips-section">
        <h4>💡 Quick Tips for Demo</h4>
        <ul>
          <li>Use the stress test button to quickly show system capabilities</li>
          <li>Manually fail nodes to show real-time detection</li>
          <li>Watch durability drop as nodes fail</li>
          <li>Trigger repair to show automatic recovery</li>
          <li>Refresh metrics to see live updates</li>
        </ul>
      </div>
    </div>
  );
}

export default ControlPanel;
