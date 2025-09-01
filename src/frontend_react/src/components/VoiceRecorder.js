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
      // Check if mediaDevices is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Your browser does not support audio recording. Please use a modern browser like Chrome, Firefox, or Edge.');
      }

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
      
      // Provide more specific error messages
      let errorMessage = 'Unable to access microphone. ';
      
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        errorMessage += 'Please allow microphone access in your browser settings:\n\n';
        errorMessage += '1. Click the lock/info icon in the address bar\n';
        errorMessage += '2. Find "Microphone" in the permissions\n';
        errorMessage += '3. Set it to "Allow"\n';
        errorMessage += '4. Refresh the page';
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        errorMessage += 'No microphone found. Please connect a microphone and try again.';
      } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
        errorMessage += 'Microphone is already in use by another application.';
      } else if (error.name === 'OverconstrainedError' || error.name === 'ConstraintNotSatisfiedError') {
        errorMessage += 'Microphone settings are not supported.';
      } else if (error.message) {
        errorMessage = error.message;
      } else {
        errorMessage += 'Please check your browser settings and try again.';
      }
      
      alert(errorMessage);
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