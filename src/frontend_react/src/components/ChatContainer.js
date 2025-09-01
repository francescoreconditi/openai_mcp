import React, { useEffect, useRef } from 'react';
import Message from './Message';
import '../styles/ChatContainer.css';

function ChatContainer({ messages, isLoading }) {
  const containerRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chat-container" ref={containerRef}>
      {messages.map((message, index) => (
        <Message key={index} message={message} />
      ))}
      
      {isLoading && (
        <div className="loading-message">
          <div className="loading-spinner"></div>
          <span>Thinking...</span>
        </div>
      )}
    </div>
  );
}

export default ChatContainer;