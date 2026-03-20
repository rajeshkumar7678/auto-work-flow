import os
import textwrap

def generate_srt(text, audio_duration, output_path="assets/captions.srt", words_per_caption=3):
    """
    Generates sentence-aware SRT captions. 
    Detects punctuation to insert natural pauses and sync with the voiceover.
    """
    import re
    # Split by sentences (keeping punctuation)
    sentences = re.split('([.!?]+)', text)
    processed_sentences = []
    for i in range(0, len(sentences)-1, 2):
        processed_sentences.append(sentences[i] + sentences[i+1])
    if len(sentences) % 2 != 0 and sentences[-1].strip():
        processed_sentences.append(sentences[-1])
        
    total_words = len(text.split())
    if total_words == 0: return None
    
    # Configuration for pauses
    pause_per_sentence = 0.4 # Seconds of silence between sentences
    total_pause_time = len(processed_sentences) * pause_per_sentence
    
    # Calculate duration per word excluding pause time
    usable_duration = audio_duration - total_pause_time
    if usable_duration < 0: # Fallback if text is too long for duration
        usable_duration = audio_duration * 0.8
        pause_per_sentence = (audio_duration * 0.2) / len(processed_sentences)
        
    duration_per_word = usable_duration / total_words
    
    captions = []
    current_time = 0.0
    
    for sentence in processed_sentences:
        s_words = sentence.split()
        if not s_words: continue
        
        # Calculate how much time the words in this sentence take
        s_narration_dur = len(s_words) * duration_per_word
        s_duration_per_word = s_narration_dur / len(s_words)
        
        for i in range(0, len(s_words), words_per_caption):
            chunk = s_words[i:i + words_per_caption]
            chunk_text = " ".join(chunk)
            
            # Duration for this chunk
            chunk_duration = len(chunk) * s_duration_per_word
            
            start_time = format_srt_time(current_time)
            end_time = format_srt_time(current_time + chunk_duration)
            
            captions.append(f"{len(captions) // 4 + 1}")
            captions.append(f"{start_time} --> {end_time}")
            captions.append(chunk_text.upper())
            captions.append("")
            
            current_time += chunk_duration
            
        # Add the sentence pause after the last word of the sentence
        current_time += pause_per_sentence

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(captions))
        
    return output_path

def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds * 1000) % 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

if __name__ == "__main__":
    script_path = "assets/script.txt"
    os.makedirs("assets", exist_ok=True)
    
    if not os.path.exists(script_path):
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("Did you know your brain makes decisions before you do? It's true! Scientists have found that your subconscious mind starts acting seconds before you even realize you've made a choice.")
            
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    print("Generating captions...")
    result = generate_srt(content, audio_duration=10.0) # Test with 10s duration
    print(f"Captions saved to: {result}")
