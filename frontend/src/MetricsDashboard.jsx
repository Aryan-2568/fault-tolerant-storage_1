import React from 'react';
import './MetricsDashboard.css';

function MetricsDashboard({ status }) {
  const durability = status.durability_percentage || 100;
  const getDurabilityColor = (val) => {
    if (val >= 99.5) return '#44ff44';
    if (val >= 95) return '#ffff44';
    if (val >= 90) return '#ffaa00';
    return '#ff4444';
  };

  const MetricCard = ({ title, value, unit = '', color = '#44ff44', icon = '' }) => (
    <div className="metric-card">
      <div className="metric-icon">{icon}</div>
      <div className="metric-title">{title}</div>
      <div className="metric-value" style={{ color }}>
        {value}
        {unit && <span className="metric-unit">{unit}</span>}
      </div>
    </div>
  );

  return (
    <div className="metrics-dashboard">
      <h2>📊 Cluster Metrics</h2>
      
      <div className="metrics-grid">
        <MetricCard
          title="Durability"
          value={durability.toFixed(1)}
          unit="%"
          color={getDurabilityColor(durability)}
          icon="🛡️"
        />
        
        <MetricCard
          title="Active Nodes"
          value={status.alive_nodes}
          unit={`/${status.total_nodes}`}
          color={status.failed_nodes > 0 ? '#ffaa00' : '#44ff44'}
          icon="🟢"
        />
        
        <MetricCard
          title="Failed Nodes"
          value={status.failed_nodes}
          color={status.failed_nodes > 0 ? '#ff4444' : '#44ff44'}
          icon="🔴"
        />
        
        <MetricCard
          title="Replication Factor"
          value={status.replication_factor}
          unit="x"
          icon="📋"
        />
        
        <MetricCard
          title="Total Objects"
          value={status.total_objects}
          icon="📦"
        />
        
        <MetricCard
          title="Storage Used"
          value={status.total_data_mb.toFixed(2)}
          unit=" MB"
          icon="💾"
        />
        
        <MetricCard
          title="Total Writes"
          value={status.total_writes}
          icon="✍️"
        />
        
        <MetricCard
          title="Total Reads"
          value={status.total_reads}
          icon="📖"
        />
      </div>

      {/* Durability Bar */}
      <div className="durability-section">
        <div className="durability-header">
          <h3>System Durability</h3>
          <span className="durability-percentage">{durability.toFixed(2)}%</span>
        </div>
        <div className="durability-bar-container">
          <div
            className="durability-bar-fill"
            style={{
              width: `${Math.min(durability, 100)}%`,
              backgroundColor: getDurabilityColor(durability)
            }}
          />
        </div>
        <div className="durability-threshold-line" style={{ left: '99.5%' }}>
          <span className="threshold-label">99.5% Target</span>
        </div>
      </div>

      {/* Replica Distribution */}
      <div className="replica-section">
        <h3>📊 Replica Distribution</h3>
        <div className="replica-grid">
          {status.nodes && status.nodes.map((node) => (
            <div
              key={node.node_id}
              className={`replica-card ${node.is_alive ? 'alive' : 'dead'}`}
            >
              <div className="replica-node-id">{node.node_id}</div>
              <div className="replica-count">{node.total_replicas}</div>
              <div className="replica-label">replicas</div>
              {node.failed_replicas > 0 && (
                <div className="replica-failed">
                  {node.failed_replicas} corrupted
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Storage per Node */}
      <div className="storage-section">
        <h3>💾 Storage per Node</h3>
        <div className="storage-bars">
          {status.nodes && status.nodes.map((node) => (
            <div key={node.node_id} className="storage-bar-item">
              <div className="storage-label">{node.node_id}</div>
              <div className="storage-bar-wrapper">
                <div
                  className={`storage-bar ${node.is_alive ? 'active' : 'inactive'}`}
                  style={{ width: `${(node.storage_used_mb / 10) * 100}%` }}
                />
              </div>
              <div className="storage-size">{node.storage_used_mb.toFixed(1)} MB</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default MetricsDashboard;
