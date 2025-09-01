import React, { useState, useEffect } from 'react';
import ChatContainer from './components/ChatContainer';
import MessageInput from './components/MessageInput';
import Sidebar from './components/Sidebar';
import VoiceRecorder from './components/VoiceRecorder';
import { chatService } from './services/chatService';
import { healthService } from './services/healthService';
import './styles/App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [useTools, setUseTools] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState({ online: false, info: {} });
  const [mcpStatus, setMcpStatus] = useState({ online: false, tools: 0 });

  // Check backend and MCP status
  useEffect(() => {
    const checkStatus = async () => {
      const status = await healthService.checkBackendHealth();
      setBackendStatus(status);
      
      if (status.online && status.info) {
        const mcpIntegration = status.info.mcp_integration || '';
        
        if (mcpIntegration.includes('subprocess')) {
          // Subprocess mode - MCP integrated
          const toolsLoaded = status.info.tools_loaded || 0;
          setMcpStatus({ online: toolsLoaded > 0, tools: toolsLoaded });
        } else {
          // Separate server mode
          const mcpHealth = await healthService.checkMcpHealth();
          setMcpStatus({ online: mcpHealth, tools: mcpHealth ? 5 : 0 });
        }
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 5000); // Check every 5 seconds
    
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (message) => {
    if (!message.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(message, conversationId, useTools);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Add assistant message
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toLocaleTimeString(),
        tools_used: response.tools_used
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setConversationId(response.conversation_id);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceTranscription = (transcribedText) => {
    if (transcribedText) {
      handleSendMessage(transcribedText);
    }
  };

  const handleClearConversation = () => {
    setMessages([]);
    setConversationId(null);
  };

  return (
    <div className="app">
      <Sidebar 
        useTools={useTools}
        onToggleTools={setUseTools}
        onClearConversation={handleClearConversation}
        backendStatus={backendStatus}
        mcpStatus={mcpStatus}
      />
      
      <div className="main-content">
        <header className="app-header">
          <h1>💬 Chat with OpenAI powered by MCP tools 🔧</h1>
        </header>
        
        <ChatContainer 
          messages={messages}
          isLoading={isLoading}
        />
        
        <div className="input-section">
          <VoiceRecorder 
            onTranscription={handleVoiceTranscription}
          />
          <MessageInput 
            onSendMessage={handleSendMessage}
            disabled={isLoading}
          />
        </div>
      </div>
    </div>
  );
}

export default App;