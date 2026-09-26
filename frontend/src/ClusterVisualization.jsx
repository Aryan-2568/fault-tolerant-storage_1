import React from 'react';
import './ClusterVisualization.css';

function ClusterVisualization({ status }) {
  const nodes = status.nodes || [];
  const numNodes = nodes.length;
  
  // Arrange nodes in a circle
  const angles = nodes.map((_, i) => (i * 360) / numNodes);
  
  const getNodeColor = (node) => {
    if (!node.is_alive) return '#ff4444'; // Red for dead
    if (node.failed_replicas > 0) return '#ffaa00'; // Orange for damaged
    return '#44ff44'; // Green for healthy
  };

  const getNodeStatus = (node) => {
    if (!node.is_alive) return 'DEAD';
    if (node.failed_replicas > 0) return 'DAMAGED';
    return 'HEALTHY';
  };

  return (
    <div className="visualization">
      <h2>🏰 Cluster Fortress</h2>
      
      <svg className="cluster-svg" viewBox="0 0 1000 800">
        {/* Grid background */}
        <defs>
          <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#e0e0e0" strokeWidth="0.5"/>
          </pattern>
          
          {/* Glow effect */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        <rect width="1000" height="800" fill="url(#grid)" />
        
        {/* Central fortress */}
        <circle cx="500" cy="400" r="120" fill="#2a2a4a" stroke="#6666ff" strokeWidth="2"/>
        <text x="500" y="410" textAnchor="middle" className="fortress-label">
          VAULT
        </text>
        
        {/* Connection lines from vault to nodes */}
        {nodes.map((node, i) => {
          const angle = angles[i];
          const rad = (angle * Math.PI) / 180;
          const x = 500 + Math.cos(rad) * 250;
          const y = 400 + Math.sin(rad) * 250;
          
          return (
            <line
              key={`line-${i}`}
              x1="500"
              y1="400"
              x2={x}
              y2={y}
              stroke={node.is_alive ? '#66ff66' : '#ff6666'}
              strokeWidth="1.5"
              opacity="0.5"
              className={node.is_alive ? 'line-active' : 'line-dead'}
            />
          );
        })}
        
        {/* Node elements */}
        {nodes.map((node, i) => {
          const angle = angles[i];
          const rad = (angle * Math.PI) / 180;
          const x = 500 + Math.cos(rad) * 250;
          const y = 400 + Math.sin(rad) * 250;
          const color = getNodeColor(node);
          const status = getNodeStatus(node);
          
          return (
            <g key={node.node_id} className="node-group">
              {/* Node shadow effect */}
              <circle
                cx={x}
                cy={y}
                r="35"
                fill="none"
                stroke={color}
                strokeWidth="8"
                opacity="0.2"
                className={!node.is_alive ? 'pulse-dead' : ''}
              />
              
              {/* Main node circle */}
              <circle
                cx={x}
                cy={y}
                r="28"
                fill={color}
                stroke="#fff"
                strokeWidth="2"
                filter="url(#glow)"
                className={node.is_alive && status !== 'DAMAGED' ? 'pulse-healthy' : ''}
              />
              
              {/* Node label */}
              <text
                x={x}
                y={y + 4}
                textAnchor="middle"
                className="node-label"
                fontSize="12"
              >
                {node.node_id.split('-')[1]}
              </text>
              
              {/* Status indicator below node */}
              <text
                x={x}
                y={y + 50}
                textAnchor="middle"
                className={`node-status-text status-${status.toLowerCase()}`}
                fontSize="11"
              >
                {status}
              </text>
              
              {/* Object count */}
              <text
                x={x}
                y={y + 65}
                textAnchor="middle"
                className="node-metric"
                fontSize="10"
              >
                {node.objects_stored} objects
              </text>
              
              {/* Damage indicator */}
              {node.failed_replicas > 0 && (
                <text
                  x={x}
                  y={y + 35}
                  textAnchor="middle"
                  className="damage-indicator"
                  fontSize="16"
                >
                  ⚠️
                </text>
              )}
              
              {/* Dead indicator */}
              {!node.is_alive && (
                <text
                  x={x}
                  y={y + 35}
                  textAnchor="middle"
                  className="dead-indicator"
                  fontSize="20"
                >
                  ✗
                </text>
              )}
            </g>
          );
        })}
      </svg>
      
      <div className="visualization-legend">
        <div className="legend-item">
          <span className="legend-color healthy"></span>
          <span>Healthy Node</span>
        </div>
        <div className="legend-item">
          <span className="legend-color damaged"></span>
          <span>Damaged Node</span>
        </div>
        <div className="legend-item">
          <span className="legend-color dead"></span>
          <span>Failed Node</span>
        </div>
      </div>
    </div>
  );
}

export default ClusterVisualization;
