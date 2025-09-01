import React, { useState } from 'react';
import '../styles/Sidebar.css';

function Sidebar({ useTools, onToggleTools, onClearConversation, backendStatus, mcpStatus }) {
  const [showToolList, setShowToolList] = useState(false);
  
  return (
    <div className="sidebar">
      <h2>Settings</h2>
      
      <div className="settings-section">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={useTools}
            onChange={(e) => onToggleTools(e.target.checked)}
          />
          <span>Use MCP Tools</span>
        </label>
        <small className="help-text">Enable/disable MCP tool usage in responses</small>
      </div>
      
      <div className="divider"></div>
      
      <button 
        className="clear-button"
        onClick={onClearConversation}
      >
        🗑️ Clear Conversation
      </button>
      
      <div className="divider"></div>
      
      <div className="status-section">
        <h3>System Status</h3>
        
        <div className={`status-item ${backendStatus.online ? 'online' : 'offline'}`}>
          <span className="status-indicator"></span>
          <span>Backend: {backendStatus.online ? 'Online ✅' : 'Offline ❌'}</span>
        </div>
        
        <div className={`status-item ${mcpStatus.online ? 'online' : 'offline'}`}>
          <span className="status-indicator"></span>
          <span>
            MCP Server: {mcpStatus.online ? `Online ✅ (${mcpStatus.tools} tools)` : 'Offline ❌'}
          </span>
          {mcpStatus.online && mcpStatus.tools > 0 && (
            <button 
              className="toggle-tools-btn"
              onClick={() => setShowToolList(!showToolList)}
              aria-label="Toggle tool list"
            >
              {showToolList ? '▼' : '▶'}
            </button>
          )}
        </div>
        
        {showToolList && mcpStatus.online && mcpStatus.toolList && (
          <div className="tool-list">
            <h4>Available Tools:</h4>
            <ul>
              {mcpStatus.toolList.map((tool, index) => (
                <li key={index}>{tool}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      <div className="sidebar-footer">
        <p className="info-text">
          💡 This chatbot uses OpenAI with MCP (Model Context Protocol) tools 
          for enhanced capabilities like weather, calculations, and more.
        </p>
      </div>
    </div>
  );
}

export default Sidebar;