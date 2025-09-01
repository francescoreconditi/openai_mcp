import React from 'react';
import '../styles/Sidebar.css';

function Sidebar({ useTools, onToggleTools, onClearConversation, backendStatus, mcpStatus }) {
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
        </div>
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