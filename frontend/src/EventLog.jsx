import React from 'react';
import './EventLog.css';

function EventLog({ events }) {
  const formatTime = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'success':
        return '✓';
      case 'info':
        return 'ℹ';
      case 'warning':
        return '⚠';
      case 'critical':
        return '✗';
      case 'error':
        return '✗';
      default:
        return '•';
    }
  };

  const getSeverityLabel = (severity) => {
    switch (severity) {
      case 'critical':
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'success':
        return 'success';
      default:
        return 'info';
    }
  };

  return (
    <div className="event-log">
      <h2>📋 Event Log</h2>
      
      <div className="event-log-container">
        {events.length === 0 ? (
          <div className="no-events">
            <p>Waiting for events...</p>
          </div>
        ) : (
          <div className="events-list">
            {[...events].reverse().map((event, index) => (
              <div
                key={index}
                className={`event-item severity-${getSeverityLabel(event.severity)}`}
              >
                <div className="event-icon">
                  {getSeverityIcon(event.severity)}
                </div>
                <div className="event-content">
                  <div className="event-message">{event.message}</div>
                  <div className="event-meta">
                    <span className="event-type">{event.type}</span>
                    <span className="event-time">{formatTime(event.timestamp)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="event-legend">
        <div className="legend-item">
          <span className="legend-icon success">✓</span>
          <span>Success</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon info">ℹ</span>
          <span>Info</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon warning">⚠</span>
          <span>Warning</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon error">✗</span>
          <span>Error/Critical</span>
        </div>
      </div>
    </div>
  );
}

export default EventLog;
