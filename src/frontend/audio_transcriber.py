# ============================================
# FILE DI TEST/DEBUG - NON PER PRODUZIONE
# Creato da: Claude Code
# Data: 2025-09-01
# Scopo: Gestione trascrizione audio con OpenAI Whisper
# ============================================

import os
import io
import tempfile
from typing import Optional
import logging
from openai import OpenAI
import streamlit as st

logger = logging.getLogger(__name__)


class AudioTranscriber:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the audio transcriber with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required for audio transcription")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def transcribe_audio(self, audio_bytes: bytes, format: str = "webm") -> Optional[str]:
        """
        Transcribe audio bytes to text using OpenAI Whisper API.
        
        Args:
            audio_bytes: The audio data as bytes
            format: The audio format (default: webm)
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            # Open the file and send to Whisper API
            with open(tmp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="it"  # Italian, change as needed
                )
            
            # Clean up the temporary file
            os.unlink(tmp_file_path)
            
            return transcript.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None
    
    def transcribe_from_base64(self, base64_audio: str, format: str = "webm") -> Optional[str]:
        """
        Transcribe base64 encoded audio to text.
        
        Args:
            base64_audio: Base64 encoded audio string
            format: The audio format (default: webm)
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            import base64
            audio_bytes = base64.b64decode(base64_audio)
            return self.transcribe_audio(audio_bytes, format)
        except Exception as e:
            logger.error(f"Error decoding base64 audio: {str(e)}")
            return None


@st.cache_resource
def get_transcriber():
    """Get a cached instance of the audio transcriber."""
    try:
        return AudioTranscriber()
    except ValueError as e:
        logger.warning(f"Could not initialize audio transcriber: {e}")
        return None