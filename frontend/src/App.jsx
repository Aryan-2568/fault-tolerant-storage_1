import React, { useState, useEffect } from 'react';
import './App.css';
import ClusterVisualization from './ClusterVisualization';
import MetricsDashboard from './MetricsDashboard';
import ControlPanel from './ControlPanel';
import EventLog from './EventLog';

function App() {
  const [clusterStatus, setClusterStatus] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE = 'http://localhost:8000/api';

  // Fetch cluster status every 2 seconds
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/cluster/status`);
        const data = await response.json();
        setClusterStatus(data);
        setError(null);
      } catch (err) {
        setError('Failed to connect to backend');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  // Fetch events every 3 seconds
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch(`${API_BASE}/cluster/events`);
        const data = await response.json();
        setEvents(data.events || []);
      } catch (err) {
        console.error('Failed to fetch events:', err);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 3000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div className="app error-container">
        <h1>⚠️ Connection Error</h1>
        <p>{error}</p>
        <p>Make sure the backend is running: <code>python app.py</code></p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🏰 BitFortress</h1>
          <p>Distributed Storage with Fault Tolerance</p>
        </div>
        {clusterStatus && (
          <div className="header-status">
            <span className="status-badge alive">
              ✓ {clusterStatus.alive_nodes} Nodes Online
            </span>
            <span className="status-badge failed">
              ✗ {clusterStatus.failed_nodes} Failed
            </span>
          </div>
        )}
      </header>

      <div className="app-content">
        <div className="top-section">
          <div className="metrics-wrapper">
            {clusterStatus && <MetricsDashboard status={clusterStatus} />}
          </div>
          <div className="control-wrapper">
            <ControlPanel API_BASE={API_BASE} />
          </div>
        </div>

        <div className="visualization-wrapper">
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <p>Initializing cluster...</p>
            </div>
          ) : clusterStatus ? (
            <ClusterVisualization status={clusterStatus} />
          ) : null}
        </div>

        <div className="bottom-section">
          <EventLog events={events} />
        </div>
      </div>
    </div>
  );
}

export default App;
