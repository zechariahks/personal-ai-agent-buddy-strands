import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User } from 'lucide-react';

const ChatInterface = ({ endpoint }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(`session-${Date.now()}`);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (message, isQuickAction = false) => {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${endpoint}/invoke`, {
        message: message,
        session_id: sessionId,
        context: {}
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.data.response,
        timestamp: new Date().toLocaleTimeString(),
        metadata: response.data.metadata
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Error: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const quickActions = [
    "What's the weather in New York?",
    "Show my calendar events",
    "Post a Bible verse",
    "What can you help me with?",
    "Check your status"
  ];

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>💬 Chat with Your AI Agent</h2>
        <span className="session-id">Session: {sessionId}</span>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <Bot size={48} />
            <h3>Welcome to your Strands AI Agent!</h3>
            <p>I can help you with weather, calendar, social media, and more. Try one of the quick actions below or ask me anything!</p>
            
            <div className="quick-actions">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  className="quick-action-btn"
                  onClick={() => sendMessage(action, true)}
                  disabled={isLoading}
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-header">
              {message.type === 'user' ? <User size={20} /> : <Bot size={20} />}
              <span className="timestamp">{message.timestamp}</span>
            </div>
            <div className="message-content">
              {message.type === 'bot' ? (
                <ReactMarkdown>{message.content}</ReactMarkdown>
              ) : (
                <p>{message.content}</p>
              )}
            </div>
            {message.metadata && (
              <div className="message-metadata">
                <small>
                  Agent: {message.metadata.agent_type} | 
                  Context: {message.metadata.context_memory_size} items
                </small>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="message bot loading">
            <div className="message-header">
              <Bot size={20} />
              <span className="timestamp">Now</span>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="message-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message here..."
          disabled={isLoading}
          className="message-input"
        />
        <button
          type="submit"
          disabled={isLoading || !inputMessage.trim()}
          className="send-button"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;