import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const MCP_URL = process.env.REACT_APP_MCP_URL || 'http://localhost:8001';

class HealthService {
  async checkBackendHealth() {
    try {
      const response = await axios.get(`${BACKEND_URL}/health`, {
        timeout: 2000
      });
      
      if (response.status === 200) {
        return {
          online: true,
          info: response.data
        };
      }
      
      return { online: false, info: {} };
    } catch (error) {
      return { online: false, info: {} };
    }
  }

  async checkMcpHealth() {
    try {
      const response = await axios.get(`${MCP_URL}/health`, {
        timeout: 2000
      });
      
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
}

export const healthService = new HealthService();