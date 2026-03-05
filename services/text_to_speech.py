
# ============= services/text_to_speech.py =============
"""Text-to-Speech Service"""
from gtts import gTTS
from pathlib import Path
import hashlib

class TextToSpeechService:
    def __init__(self):
        self.audio_dir = Path("static/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_speech(self, text, language='en'):
        # Generate filename
        text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
        filename = f"tts_{language}_{text_hash}.mp3"
        filepath = self.audio_dir / filename
        
        # Check cache
        if filepath.exists():
            return filename
        
        # Generate speech
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(str(filepath))
        
        return filename

