import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

class ChatService {
  async sendMessage(message, conversationId = null, useTools = true) {
    try {
      const response = await axios.post(
        `${BACKEND_URL}/chat`,
        {
          message,
          conversation_id: conversationId,
          use_tools: useTools
        },
        {
          timeout: 60000, // 60 second timeout
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Chat service error:', error);
      
      if (error.response) {
        // Server responded with error
        return { error: error.response.data.detail || 'Server error occurred' };
      } else if (error.request) {
        // No response received
        return { error: 'No response from server. Please check if backend is running.' };
      } else {
        // Request setup error
        return { error: error.message };
      }
    }
  }
}

export const chatService = new ChatService();