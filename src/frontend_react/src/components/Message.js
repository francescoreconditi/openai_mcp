import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import '../styles/Message.css';

function Message({ message }) {
  const [showTools, setShowTools] = useState(false);
  const isUser = message.role === 'user';

  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'} ${message.isError ? 'error-message' : ''}`}>
      <div className="message-header">
        <span className="message-role">
          {isUser ? '👤 You' : '🤖 Assistant'}
        </span>
        <span className="message-timestamp">{message.timestamp}</span>
      </div>
      
      <div className="message-content">
        <ReactMarkdown
          components={{
            code({node, inline, className, children, ...props}) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>
      
      {message.tools_used && message.tools_used.length > 0 && (
        <div className="tools-section">
          <button 
            className="tools-toggle"
            onClick={() => setShowTools(!showTools)}
          >
            🔧 Tools used ({message.tools_used.length})
          </button>
          
          {showTools && (
            <ul className="tools-list">
              {message.tools_used.map((tool, idx) => (
                <li key={idx}>{tool}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default Message;