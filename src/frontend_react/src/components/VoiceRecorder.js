import React, { useState, useRef } from 'react';
import { audioService } from '../services/audioService';
import '../styles/VoiceRecorder.css';

function VoiceRecorder({ onTranscription }) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Please allow microphone access to use voice input');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async () => {
    if (!audioBlob) return;

    setIsTranscribing(true);
    try {
      const transcription = await audioService.transcribeAudio(audioBlob);
      if (transcription) {
        onTranscription(transcription);
        setAudioBlob(null); // Clear after successful transcription
      } else {
        alert('Failed to transcribe audio. Please try again.');
      }
    } catch (error) {
      console.error('Transcription error:', error);
      alert('Error transcribing audio: ' + error.message);
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setAudioBlob(file);
  };

  return (
    <div className="voice-recorder">
      <div className="recorder-controls">
        {!isRecording ? (
          <button 
            className="record-button"
            onClick={startRecording}
            disabled={isTranscribing}
          >
            🎤 Start Recording
          </button>
        ) : (
          <button 
            className="record-button recording"
            onClick={stopRecording}
          >
            ⏹️ Stop Recording
          </button>
        )}

        <input
          type="file"
          accept="audio/*"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
          id="audio-file-input"
        />
        <label htmlFor="audio-file-input" className="upload-button">
          📁 Upload Audio
        </label>
      </div>

      {audioBlob && (
        <div className="audio-preview">
          <audio controls src={URL.createObjectURL(audioBlob)} />
          <button 
            className="transcribe-button"
            onClick={transcribeAudio}
            disabled={isTranscribing}
          >
            {isTranscribing ? '⏳ Transcribing...' : '📝 Transcribe'}
          </button>
        </div>
      )}
    </div>
  );
}

export default VoiceRecorder;