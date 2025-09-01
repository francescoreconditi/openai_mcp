import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

class AudioService {
  async transcribeAudio(audioBlob) {
    try {
      // Create FormData to send audio file
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      // Send to backend for transcription
      const response = await axios.post(
        `${BACKEND_URL}/transcribe`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          timeout: 30000 // 30 second timeout for transcription
        }
      );

      if (response.data && response.data.text) {
        return response.data.text;
      }

      return null;
    } catch (error) {
      console.error('Audio transcription error:', error);
      
      // For now, if transcription endpoint doesn't exist, return a placeholder
      if (error.response && error.response.status === 404) {
        console.warn('Transcription endpoint not found. Using placeholder text.');
        return '[Voice transcription not yet implemented - please type your message]';
      }
      
      throw error;
    }
  }

  // Alternative: Direct OpenAI API call (requires API key in frontend - not recommended for production)
  async transcribeAudioDirect(audioBlob, apiKey) {
    if (!apiKey) {
      throw new Error('OpenAI API key required for transcription');
    }

    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.webm');
    formData.append('model', 'whisper-1');

    try {
      const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`
        },
        body: formData
      });

      const data = await response.json();
      return data.text;
    } catch (error) {
      console.error('Direct OpenAI transcription error:', error);
      throw error;
    }
  }
}

export const audioService = new AudioService();