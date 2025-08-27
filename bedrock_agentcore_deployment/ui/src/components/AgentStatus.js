import React from 'react';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

const AgentStatus = ({ status }) => {
  if (!status) {
    return (
      <div className="agent-status">
        <h3>Agent Status</h3>
        <div className="status-item">
          <Clock size={16} />
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  const getStatusIcon = (isHealthy) => {
    return isHealthy ? <CheckCircle size={16} color="green" /> : <XCircle size={16} color="red" />;
  };

  return (
    <div className="agent-status">
      <h3>🤖 Agent Status</h3>
      
      <div className="status-section">
        <h4>General Info</h4>
        <div className="status-item">
          <span className="label">Name:</span>
          <span>{status.agent_name}</span>
        </div>
        <div className="status-item">
          <span className="label">Type:</span>
          <span>{status.agent_type}</span>
        </div>
        <div className="status-item">
          <span className="label">Framework:</span>
          <span>{status.framework}</span>
        </div>
        <div className="status-item">
          <span className="label">Deployment:</span>
          <span>{status.deployment}</span>
        </div>
      </div>

      <div className="status-section">
        <h4>Specialist Agents</h4>
        {Object.entries(status.specialist_agents || {}).map(([key, name]) => (
          <div key={key} className="status-item">
            {getStatusIcon(true)}
            <span>{key}: {name}</span>
          </div>
        ))}
      </div>

      <div className="status-section">
        <h4>Memory & Context</h4>
        <div className="status-item">
          <span className="label">Context Memory:</span>
          <span>{status.context_memory} items</span>
        </div>
        <div className="status-item">
          <span className="label">Decision History:</span>
          <span>{status.decision_history} decisions</span>
        </div>
      </div>

      <div className="status-section">
        <h4>Last Updated</h4>
        <div className="status-item">
          <Clock size={16} />
          <span>{new Date(status.timestamp).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};

export default AgentStatus;