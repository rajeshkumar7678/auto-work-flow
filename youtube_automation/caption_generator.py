import os
import textwrap
import re

def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds * 1000) % 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_srt(text=None, audio_duration=None, output_path="assets/captions.srt", words_per_caption=1, audio_path=None):
    """
    Generates sentence-aware SRT captions.
    Tries to use Whisper for precise word-level timestamps.
    Falls back to heuristic sync if Whisper fails.
    """
    if audio_path:
        try:
            import whisper
            print("🎙️ Generating precise word-by-word captions using Whisper...")
            # Load tiny or base model for speed
            model = whisper.load_model("base")
            result = model.transcribe(audio_path, word_timestamps=True)
            
            captions = []
            index = 1
            for segment in result.get("segments", []):
                for word_info in segment.get("words", []):
                    start = format_srt_time(word_info["start"])
                    end = format_srt_time(word_info["end"])
                    word_text = word_info["word"].strip().upper()
                    
                    if not word_text:
                        continue
                        
                    captions.append(str(index))
                    captions.append(f"{start} --> {end}")
                    captions.append(word_text)
                    captions.append("")
                    index += 1
                    
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(captions))
                
            return output_path
        except ImportError:
            print("⚠️ 'openai-whisper' not installed. Falling back to heuristic sync.")
        except Exception as e:
            print(f"⚠️ Whisper failed: {e}. Falling back to heuristic sync.")

    # --- FALLBACK HEURISTIC SYNC ---
    if not text or not audio_duration:
        print("❌ Cannot generate captions without text/audio_duration fallback.")
        return None
        
    print("🎙️ Generating captions using heuristic sync (1 word per caption)...")
    sentences = re.split('([.!?]+)', text)
    processed_sentences = []
    for i in range(0, len(sentences)-1, 2):
        processed_sentences.append(sentences[i] + sentences[i+1])
    if len(sentences) % 2 != 0 and sentences[-1].strip():
        processed_sentences.append(sentences[-1])
        
    total_words = len(text.split())
    if total_words == 0: return None
    
    pause_per_sentence = 0.4
    total_pause_time = len(processed_sentences) * pause_per_sentence
    
    usable_duration = audio_duration - total_pause_time
    if usable_duration < 0:
        usable_duration = audio_duration * 0.8
        pause_per_sentence = (audio_duration * 0.2) / len(processed_sentences)
        
    duration_per_word = usable_duration / total_words
    
    captions = []
    current_time = 0.0
    index = 1
    
    for sentence in processed_sentences:
        s_words = sentence.split()
        if not s_words: continue
        
        s_narration_dur = len(s_words) * duration_per_word
        s_duration_per_word = s_narration_dur / len(s_words)
        
        for i in range(0, len(s_words), words_per_caption):
            chunk = s_words[i:i + words_per_caption]
            chunk_text = " ".join(chunk)
            
            chunk_duration = len(chunk) * s_duration_per_word
            start_time = format_srt_time(current_time)
            end_time = format_srt_time(current_time + chunk_duration)
            
            captions.append(str(index))
            captions.append(f"{start_time} --> {end_time}")
            captions.append(chunk_text.upper())
            captions.append("")
            
            current_time += chunk_duration
            index += 1
            
        current_time += pause_per_sentence

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(captions))
        
    return output_path

if __name__ == "__main__":
    pass
