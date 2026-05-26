import os
import asyncio
import edge_tts
from dotenv import load_dotenv

load_dotenv()

# Change this voice anytime — no API key needed!
# Great cinematic options: en-US-AndrewNeural, en-US-GuyNeural, en-US-JennyNeural
DEFAULT_EDGE_VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-AndrewNeural")


async def _edge_tts_generate(text: str, voice: str, output_path: str):
    # Added rate and pitch for a deeper, cinematic storytelling feel
    communicate = edge_tts.Communicate(text, voice, rate="-10%", pitch="-5Hz")
    await communicate.save(output_path)


def generate_voice(text, output_path="assets/voice.mp3", language="English"):
    """
    Text → Speech Pipeline (priority order):
    1. ElevenLabs  — if ELEVENLABS_API_KEY is set and valid
    2. Edge TTS    — FREE, natural neural voices (default fallback)
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "sk_e010953bb85a9c3cc92f7f80b88ce7d81d9c869d9fc092ec")

    # --- Try ElevenLabs first ---
    if api_key:
        try:
            from elevenlabs.client import ElevenLabs
            client = ElevenLabs(api_key=api_key)
            audio = client.text_to_speech.convert(
                text=text,
                voice_id=elevenlabs_voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            with open(output_path, "wb") as f:
                for chunk in audio:
                    if chunk:
                        f.write(chunk)
            print("✅ Voice generated via ElevenLabs.")
            return output_path
        except Exception as e:
            print(f"⚠️  ElevenLabs failed ({type(e).__name__}). Switching to Edge TTS...")

    # --- Fallback: Microsoft Edge TTS (FREE, neural quality) ---
    # Map language to Edge TTS voice
    voice_map = {
        "English": os.getenv("EDGE_TTS_VOICE", "en-US-AndrewNeural"),
        "Hindi": "hi-IN-MadhurNeural",
    }
    voice = voice_map.get(language, "en-US-AndrewNeural")
    
    print(f"🎙️  Generating voice via Microsoft Edge TTS (voice: {voice}, language: {language})...")
    asyncio.run(_edge_tts_generate(text, voice, output_path))
    print(f"✅ Voice generated via Edge TTS and saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    script_path = "assets/script.txt"

    if not os.path.exists(script_path):
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(
                "Did you know your brain makes decisions before you do? "
                "Scientists found your subconscious acts seconds before "
                "you even realize you've made a choice. Mind-blowing, right?"
            )

    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()

    print("Testing voice generation...")
    try:
        result_path = generate_voice(script_text)
        print(f"Done! File saved at: {result_path}")
    except Exception as e:
        print(f"Error: {e}")
