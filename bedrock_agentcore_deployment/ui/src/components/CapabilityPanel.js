import React, { useState } from 'react';
import axios from 'axios';
import { Cloud, Calendar, MessageCircle, Mail, Brain, Play } from 'lucide-react';

const CapabilityPanel = ({ capabilities, endpoint }) => {
  const [activeCapability, setActiveCapability] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const getCapabilityIcon = (name) => {
    switch (name) {
      case 'weather': return <Cloud size={20} />;
      case 'calendar': return <Calendar size={20} />;
      case 'social': return <MessageCircle size={20} />;
      case 'email': return <Mail size={20} />;
      case 'decision': return <Brain size={20} />;
      default: return <Play size={20} />;
    }
  };

  const executeCapability = async (capability, params = {}) => {
    setLoading(true);
    setActiveCapability(capability.name);
    
    try {
      let response;
      
      switch (capability.name) {
        case 'weather':
          response = await axios.post(`${endpoint}/weather`, {
            city: params.city || 'New York'
          });
          break;
        case 'calendar':
          response = await axios.post(`${endpoint}/calendar`, {
            action: params.action || 'show events'
          });
          break;
        case 'social':
          response = await axios.post(`${endpoint}/social`, {
            action: params.action || 'post bible verse'
          });
          break;
        default:
          response = await axios.post(`${endpoint}/invoke`, {
            message: `Use ${capability.name} capability`,
            session_id: `capability-${Date.now()}`
          });
      }
      
      setResult({
        capability: capability.name,
        success: true,
        data: response.data
      });
    } catch (error) {
      setResult({
        capability: capability.name,
        success: false,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setLoading(false);
      setActiveCapability(null);
    }
  };

  const quickActions = {
    weather: [
      { label: 'Weather in NYC', params: { city: 'New York' } },
      { label: 'Weather in London', params: { city: 'London' } },
      { label: 'Weather in Tokyo', params: { city: 'Tokyo' } }
    ],
    calendar: [
      { label: 'Show Events', params: { action: 'show events' } },
      { label: 'Today\'s Schedule', params: { action: 'today' } }
    ],
    social: [
      { label: 'Post Bible Verse', params: { action: 'post bible verse' } },
      { label: 'Check X Status', params: { action: 'status' } }
    ]
  };

  return (
    <div className="capability-panel">
      <h3>🚀 Agent Capabilities</h3>
      
      <div className="capabilities-list">
        {capabilities.map((capability) => (
          <div key={capability.name} className="capability-item">
            <div className="capability-header">
              {getCapabilityIcon(capability.name)}
              <div>
                <h4>{capability.name}</h4>
                <p>{capability.description}</p>
                <small>Agent: {capability.agent}</small>
              </div>
            </div>
            
            <div className="capability-actions">
              <button
                onClick={() => executeCapability(capability)}
                disabled={loading}
                className="test-btn"
              >
                {loading && activeCapability === capability.name ? 'Testing...' : 'Test'}
              </button>
              
              {quickActions[capability.name] && (
                <div className="quick-actions">
                  {quickActions[capability.name].map((action, index) => (
                    <button
                      key={index}
                      onClick={() => executeCapability(capability, action.params)}
                      disabled={loading}
                      className="quick-action-btn small"
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {result && (
        <div className={`capability-result ${result.success ? 'success' : 'error'}`}>
          <h4>Result: {result.capability}</h4>
          {result.success ? (
            <div className="result-content">
              {typeof result.data === 'string' ? (
                <p>{result.data}</p>
              ) : (
                <pre>{JSON.stringify(result.data, null, 2)}</pre>
              )}
            </div>
          ) : (
            <div className="error-content">
              <p>Error: {result.error}</p>
            </div>
          )}
          <button onClick={() => setResult(null)} className="close-btn">
            Close
          </button>
        </div>
      )}
    </div>
  );
};

export default CapabilityPanel;