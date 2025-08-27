import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatInterface from './components/ChatInterface';
import AgentStatus from './components/AgentStatus';
import CapabilityPanel from './components/CapabilityPanel';
import './App.css';

const App = () => {
  const [agentEndpoint, setAgentEndpoint] = useState(
    process.env.REACT_APP_AGENT_ENDPOINT || 'http://localhost:8000'
  );
  const [agentStatus, setAgentStatus] = useState(null);
  const [capabilities, setCapabilities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgentInfo();
  }, [agentEndpoint]);

  const fetchAgentInfo = async () => {
    try {
      setLoading(true);
      const [statusRes, capRes] = await Promise.all([
        axios.get(`${agentEndpoint}/status`),
        axios.get(`${agentEndpoint}/capabilities`)
      ]);
      
      setAgentStatus(statusRes.data);
      setCapabilities(capRes.data.capabilities || []);
    } catch (error) {
      console.error('Failed to fetch agent info:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 Strands Personal AI Agent</h1>
        <p>Powered by Amazon Bedrock AgentCore</p>
        
        <div className="endpoint-config">
          <label>
            Agent Endpoint:
            <input
              type="text"
              value={agentEndpoint}
              onChange={(e) => setAgentEndpoint(e.target.value)}
              placeholder="https://your-agentcore-endpoint"
            />
          </label>
          <button onClick={fetchAgentInfo}>Connect</button>
        </div>
      </header>

      {loading ? (
        <div className="loading">Loading agent information...</div>
      ) : (
        <div className="app-content">
          <div className="sidebar">
            <AgentStatus status={agentStatus} />
            <CapabilityPanel 
              capabilities={capabilities} 
              endpoint={agentEndpoint}
            />
          </div>
          
          <div className="main-content">
            <ChatInterface endpoint={agentEndpoint} />
          </div>
        </div>
      )}
    </div>
  );
};

export default App;