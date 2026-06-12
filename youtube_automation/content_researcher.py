import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Setup standard console output encoding for Windows compatibility
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

class ContentResearcher:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")

    def research_topic(self, topic):
        """
        Researches real-time football facts, stats, and records using the Gemini API
        with built-in Google Search grounding retrieval.
        """
        if not self.gemini_key:
            print("⚠️ No GEMINI_API_KEY found. Content research falling back to local heuristic.")
            return self._fallback_research(topic)

        print(f"🔍 Researching football facts for: '{topic}' using Google Search Grounding...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        
        prompt = f"""
        Research the topic: '{topic}'
        We are creating a high-retention football YouTube Short. 
        Search the web and gather:
        1. 3-5 interesting, real facts about this match/event/player.
        2. Real-time statistics (score, lineups, dates, goal scorers, or recent form).
        3. Historic records broken or relevant histories between the teams/players.
        4. A brief, high-energy summary.

        Return ONLY a JSON object with this exact structure:
        {{
          "topic": "{topic}",
          "facts": [
            "Fact 1 details",
            "Fact 2 details",
            "Fact 3 details"
          ],
          "stats": [
             "Stat 1 details",
             "Stat 2 details"
          ],
          "records": [
             "Record 1 details"
          ],
          "summary": "High energy summary"
        }}
        """

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "tools": [{"google_search": {}}]  # Google Search grounding in v1beta
        }

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
            if response.status_code == 200:
                data = response.json()
                # Extract text response from Gemini contents
                candidates = data.get("candidates", [])
                if candidates:
                    content_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    # Clean markdown code block wraps if LLM adds them
                    if "```json" in content_text:
                        content_text = content_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in content_text:
                        content_text = content_text.split("```")[1].split("```")[0].strip()
                    research_json = json.loads(content_text)
                    return research_json

                else:
                    print("⚠️ Gemini response candidate list empty.")
            else:
                print(f"⚠️ Gemini API failed with status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"⚠️ Gemini Research API Exception: {e}")

        return self._fallback_research(topic)

    def _fallback_research(self, topic):
        """
        Fallback when API key is missing or calls fail.
        Generates simulated/plausible football facts based on the topic.
        """
        print("⚠️ Running fallback sports heuristic research...")
        return {
            "topic": topic,
            "facts": [
                f"The clash between the teams created massive excitement among global fans.",
                f"Tactical adjustments and key players defined the tempo of this tournament fixture.",
                f"Stadium gates were packed with passionate supporters waving flags and cheering."
            ],
            "stats": [
                "Match statistics indicated highly competitive possession numbers.",
                "Goalkeepers on both sides made critical saves to keep the sheet close."
            ],
            "records": [
                "This fixture adds another chapter to the historic encounters between the sides."
            ],
            "summary": f"An intense sports matchup bringing together football enthusiasts around the world."
        }

if __name__ == "__main__":
    researcher = ContentResearcher()
    res = researcher.research_topic("Mexico vs South Africa")
    print(json.dumps(res, indent=4))
