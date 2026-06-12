import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def detect_topic_type(topic):
    topic = topic.lower()
    if "karma" in topic or "revenge" in topic or "justice" in topic:
        return "karma"
    if "mystery" in topic or "disappear" in topic or "unexplained" in topic or "secret" in topic:
        return "mystery"
    if "mindset" in topic or "billionaire" in topic or "success" in topic or "rich" in topic:
        return "billionaire"
    if "life lesson" in topic or "moral" in topic or "sad" in topic or "emotional" in topic:
        return "emotional"
    if "fact" in topic or "shocking" in topic or "crazy" in topic:
        return "shocking_facts"
    return "cinematic_story"

def get_specialized_prompt(topic, topic_type, language, duration, research_data=None):
    if research_data:
        # Construct facts description
        facts_str = "\n".join([f"- {f}" for f in research_data.get("facts", [])])
        stats_str = "\n".join([f"- {s}" for s in research_data.get("stats", [])])
        records_str = "\n".join([f"- {r}" for r in research_data.get("records", [])])
        summary_str = research_data.get("summary", "")
        
        # Language instructions
        if language == "Hindi":
            lang_instruction = (
                "CRITICAL: The entire script MUST be written strictly in the Devanagari script (हिन्दी लिपि). "
                "Under no circumstances should you use Latin (English) letters for Hindi text. "
                "Use clear, formal, and high-impact standard Hindi vocabulary suitable for a professional sports narrator."
            )
        else:
            lang_instruction = f"Write the script in {language}."

        # Determine word count bounds based on duration
        dur_str = str(duration).lower()
        if "2 minutes" in dur_str or "2 min" in dur_str:
            word_count_instruction = "STRICT REQUIREMENT: The script MUST be between 260 and 300 words total."
        elif "5 minutes" in dur_str or "5 min" in dur_str:
            word_count_instruction = "STRICT REQUIREMENT: The script MUST be between 650 and 750 words total."
        else:
            word_count_instruction = "STRICT REQUIREMENT: The script MUST be between 100 and 130 words total (ideal for a 45-60 second fast-paced YouTube Shorts video)."

        return f"""
Create a highly viral, fast-paced, and fact-based YouTube Shorts sports script.
Topic: {topic}
Language: {language}
Vibe/Style: Sports Documentary

Researched Facts:
{facts_str}

Researched Stats:
{stats_str}

Researched Records:
{records_str}

Context/Summary:
{summary_str}

Requirements:
- {lang_instruction}
- {word_count_instruction}
- Start with an ultra-engaging, high-energy visual sports hook in the first 3 seconds (e.g. 'Did you know Mbappe just broke another World Cup record?', 'No one expected this historic moment...').
- Incorporate exactly 3 key football facts or statistics from the research naturally. Do not write list headers or act markers.
- Keep the script fast-paced, high-retention, and completely fact-based.
- End with a strong sports channel Subscribe/Like CTA.
- Do NOT write section headers. The output must be pure, continuous narrative text ready for speaking.
"""

    # Language instructions
    if language == "Hindi":

        lang_instruction = (
            "CRITICAL: The entire script MUST be written strictly in the Devanagari script (हिन्दी लिपि). "
            "Under no circumstances should you use the Urdu/Perso-Arabic script or Latin (English) letters for Hindi text. "
            "Use clear, formal, and high-impact standard Hindi vocabulary (standard Hindi language) suitable for a professional documentary narrator."
        )
    else:
        lang_instruction = f"Write the script in {language}."

    # Determine prompt structure based on duration
    dur_str = str(duration).lower()
    
    if "2 minutes" in dur_str or "2 min" in dur_str:
        word_count_instruction = "STRICT REQUIREMENT: The script MUST be between 260 and 300 words total to fit a 2-minute video at normal speaking pace."
        prompt = f"""
Create a highly engaging, mid-form standard video script.
Topic/Vibe: {topic}
Language: {language}
Vibe/Style: {topic_type}

Requirements:
- {lang_instruction}
- {word_count_instruction}
- HOOK (0:00 - 0:10): Start with an intense, curiosity-inducing hook that sets the stage and prevents the viewer from clicking away.
- ACT I - INTRODUCTION & CONTEXT (0:10 - 0:40): Introduce the historical premise, event, or mystery. Set the background.
- ACT II - DEEPER EXPLORATION (0:40 - 1:30): Develop the narrative with 2-3 key historical beats, shocking twists, or deep insights. Build dramatic tension.
- ACT III - CLIMAX & PAYOFF (1:30 - 2:00): Deliver a powerful climax, emotional payoff, or historical resolution, ending with a high-impact final sentence.
- Flow seamlessly. Use natural transitions between parts. Do NOT write section headers like 'ACT I' or 'HOOK' in the output. The output must be pure narrative text.
"""
    elif "5 minutes" in dur_str or "5 min" in dur_str:
        word_count_instruction = "STRICT REQUIREMENT: The script MUST be between 650 and 750 words total to fit a 5-minute video at standard narration speed."
        prompt = f"""
Create a professional, documentary-style long-form video script.
Topic/Vibe: {topic}
Language: {language}
Vibe/Style: {topic_type}

Requirements:
- {lang_instruction}
- {word_count_instruction}
- INTRODUCTION & HOOK (0:00 - 0:45): Start with a dramatic premise or question. Establish a cinematic tone and introduce the topic's grand significance.
- PART 1 - HISTORICAL BACKGROUND & CONTEXT (0:45 - 2:00): Build the historical setup, detailed setting, and introduce key characters or motivations.
- PART 2 - THE CORE CONFLICT OR EVENT (2:00 - 3:30): Walk through the key turning points chronologically or logically with rich detail and suspense.
- PART 3 - REVEAL & CLIMAX (3:30 - 4:30): Bring all threads together for the major reveal, climax, or turning point.
- OUTRO & RESOLUTION (4:30 - 5:00): Synthesize the historical lesson, lasting legacy, or moral takeaway.
- Make it sound like a premium History Channel or high-production documentary narration. Do NOT write section headers or markdown titles. The output must be purely narratable, fluent paragraphs.
"""
    else: # Default/Shorts: 45-60 seconds
        word_count_instruction = "STRICT REQUIREMENT: The script MUST be between 100 and 130 words total to fit a 45-60 second fast-paced YouTube Shorts video."
        hook_instruction = "IMPORTANT: Start with a high-energy, high-impact HOOK in the first 3 seconds (e.g., 'Nobody believed him until...', 'This terrifying secret was just exposed...', 'A homeless man did this, and then...')."
        prompt = f"""
Create a highly viral, fast-paced YouTube Shorts story.
Topic/Vibe: {topic}
Language: {language}
Vibe/Style: {topic_type}

Requirements:
- {lang_instruction}
- {word_count_instruction}
- {hook_instruction}
- Focus on ONE emotional micro-story, ONE twist, and ONE emotional payoff. NO robotic lists. Make it feel cinematic.
- Do NOT write section headers. The output must be pure, continuous narrative text.
"""
    
    if topic_type == "karma":
        return prompt + "\nStyle: Karma Story. Someone does something bad or good, and they get exactly what they deserve at the end in a shocking way."
    elif topic_type == "mystery":
        return prompt + "\nStyle: Mystery. Build suspense rapidly. Reveal a shocking, terrifying, or unbelievable truth at the very end."
    elif topic_type == "billionaire":
        return prompt + "\nStyle: Motivational Cinematic. A story of extreme doubt or struggle that ends in massive success or a brilliant mindset shift."
    elif topic_type == "emotional":
        return prompt + "\nStyle: Emotional Micro-Story. Touch the viewer's heart. A story of sacrifice, love, or a deep life lesson with a twist."
    elif topic_type == "shocking_facts":
        return prompt + "\nStyle: Shocking Story. Tell a cohesive story about a crazy historical event or unbelievable occurrence, not just a list of facts."
    else:
        return prompt + "\nStyle: Cinematic AI Story. Dark, moody, or inspiring narrative with a massive plot twist at the end."

def generate_script(topic, duration="45-60 seconds", language="English", research_data=None):
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = "gpt-4o-mini"
    elif provider == "grok" or provider == "groq":
        key = os.getenv("XAI_API_KEY") or os.getenv("GROQ_API_KEY")
        if key and key.startswith("gsk_"):
            client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
            model = "llama-3.3-70b-versatile"
        else:
            client = OpenAI(api_key=key, base_url="https://api.x.ai/v1")
            model = "grok-4-latest"
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    topic_type = detect_topic_type(topic)
    prompt = get_specialized_prompt(topic, topic_type, language, duration, research_data=research_data)


    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a viral YouTube content creator."},
            {"role": "user", "content": prompt}
        ]
    )

    script = response.choices[0].message.content
    
    # Sanitize: Remove markdown bolding/italics that TTS reads as "asterisk asterisk"
    script = script.replace("**", "").replace("*", "")
    
    # Save to file
    os.makedirs("assets", exist_ok=True)
    with open("assets/script.txt", "w", encoding="utf-8") as f:
        f.write(script)
    
    return script

if __name__ == "__main__":
    test_topic = "Why your brain makes decisions before you do"
    print(f"Generating script for: {test_topic} using {os.getenv('LLM_PROVIDER')}...")
    try:
        result = generate_script(test_topic)
        print("Script generated successfully!")
        print("-" * 30)
        print(result)
        print("-" * 30)
    except Exception as e:
        print(f"Error: {e}")
