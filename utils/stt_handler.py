"""Speech-to-Text handler using Groq Whisper."""
from groq import Groq
from config import GROQ_WHISPER_MODEL
from typing import BinaryIO


def transcribe_audio(audio_file: BinaryIO, groq_api_key: str) -> str:
    """
    Transcribe audio file using Groq Whisper.
    
    Args:
        audio_file: Audio file (wav, mp3, m4a, etc.)
        groq_api_key: Groq API key
    
    Returns:
        Transcribed text
    """
    try:
        client = Groq(api_key=groq_api_key)
        
        # Call Groq Whisper API
        transcription = client.audio.transcriptions.create(
            model=GROQ_WHISPER_MODEL,
            file=audio_file,
            response_format="text"
        )
        
        return transcription
    
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")
