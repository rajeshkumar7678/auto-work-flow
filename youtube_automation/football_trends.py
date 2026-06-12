import os
import requests
import json
import xml.etree.ElementTree as ET
from googleapiclient.discovery import build
from pytrends.request import TrendReq
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Setup standard console output encoding for Windows compatibility
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

class FootballTrendScout:
    def __init__(self):
        # Initialize LLM Client dynamically using LLM_PROVIDER
        provider = os.getenv("LLM_PROVIDER", "openai").lower().strip()
        if provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o-mini"
        elif provider in ["grok", "groq"]:
            key = os.getenv("XAI_API_KEY") or os.getenv("GROQ_API_KEY")
            if key and key.startswith("gsk_"):
                self.client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
                self.model = "llama-3.3-70b-versatile"
            else:
                self.client = OpenAI(api_key=key, base_url="https://api.x.ai/v1")
                self.model = "grok-4-latest"
        elif provider == "deepseek":
            self.client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
            self.model = "deepseek-chat"
        else:
            # Fallback to OpenAI
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o-mini"

    def fetch_reddit_football_trends(self):
        """
        Fetches hot titles from football-related subreddits.
        Does not require API keys (uses public JSON endpoint).
        """
        subreddits = ["soccer", "football", "worldcup", "fifacareers"]
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        items = []

        print("🔍 Scanning Reddit subreddits...")
        for sub in subreddits:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=15"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    for post in posts:
                        pdata = post.get("data", {})
                        title = pdata.get("title", "")
                        score = pdata.get("score", 0)
                        comments = pdata.get("num_comments", 0)
                        
                        # Only keep topics that have reasonable engagement
                        if score > 50 or comments > 10:
                            items.append({
                                "source": f"r/{sub}",
                                "text": title,
                                "engagement": score + (comments * 2)
                            })
            except Exception as e:
                print(f"⚠️ Reddit fetch failed for r/{sub}: {e}")
        return items

    def fetch_google_sports_trends(self):
        """
        Fetches trending sports terms in the US using pytrends.
        """
        print("🔍 Checking Google Trends...")
        trends = []
        try:
            pytrends = TrendReq(hl="en-US", tz=360)
            # Fetch daily trending searches in the US
            df = pytrends.trending_searches(pn="united_states")
            if not df.empty:
                for idx, row in df.iterrows():
                    trends.append({
                        "source": "google_trends",
                        "text": row[0],
                        "engagement": 100  # Default baseline engagement
                    })
        except Exception as e:
            print(f"⚠️ Google Trends fetch failed: {e}")
        return trends

    def fetch_youtube_sports_trending(self):
        """
        Queries YouTube API for most popular videos in Category 17 (Sports).
        """
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            print("⚠️ No YOUTUBE_API_KEY found. Skipping YouTube Sports trends.")
            return []

        print("🔍 Checking YouTube Sports Trending...")
        trends = []
        try:
            youtube = build("youtube", "v3", developerKey=api_key)
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="US",
                videoCategoryId="17",  # 17 = Sports
                maxResults=15
            )
            response = request.execute()
            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                title = snippet.get("title", "")
                view_count = int(stats.get("viewCount", 0))
                
                trends.append({
                    "source": "youtube_sports",
                    "text": title,
                    "engagement": view_count // 1000  # Normalize engagement
                })
        except Exception as e:
            print(f"⚠️ YouTube Sports trends fetch failed: {e}")
        return trends

    def fetch_espn_football_news(self):
        """
        Scrapes ESPN RSS feed for global football news.
        """
        print("🔍 Checking ESPN Football RSS Feed...")
        news = []
        url = "https://www.espn.com/espn/rss/soccer/news"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall(".//item"):
                    title = item.find("title").text
                    desc = item.find("description").text if item.find("description") is not None else ""
                    news.append({
                        "source": "espn_news",
                        "text": f"{title} - {desc}",
                        "engagement": 80
                    })
        except Exception as e:
            print(f"⚠️ ESPN RSS fetch failed: {e}")
        return news

    def get_football_trends(self):
        """
        Aggregates all sources, filters out noise, and scores the trends.
        """
        raw_items = []
        raw_items += self.fetch_reddit_football_trends()
        raw_items += self.fetch_google_sports_trends()
        raw_items += self.fetch_youtube_sports_trending()
        raw_items += self.fetch_espn_football_news()

        if not raw_items:
            print("❌ No raw sports trends fetched.")
            return []

        print(f"✅ Collected {len(raw_items)} raw data entries. Filtering and scoring using {self.model}...")

        # Construct a dense prompt for the LLM to extract structured entities and score them
        prompt = f"""
        You are an expert sports data analyst.
        Analyze the following raw trending headlines/data points from Reddit, Google, YouTube, and news feeds:
        
        {json.dumps(raw_items[:50], indent=2)}
        
        Task:
        1. Identify the Top 5 most viral, football (soccer) or FIFA World Cup related topics/players/events.
        2. Filter out non-football sports (e.g. Basketball, American Football, Baseball, Cricket).
        3. Make sure the topics represent current, active events (less than 24h old, increasing popularity).
        4. For each topic, write a concise search keyword phrase optimized for search and video generation (e.g. "Mbappe Real Madrid debut", "Messi Copa America record", "England vs Brazil penalty shootout").
        5. Assign a dynamic 'trend_score' (from 1 to 100) based on mention frequency and engagement indicators from the data.

        Return ONLY a JSON list of objects matching this structure:
        [
          {{
            "topic": "Clean Name of Topic/Player/Event",
            "search_query": "Optimized search query for stock media",
            "trend_score": 95,
            "reason": "Brief reason why this is trending"
          }}
        ]
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a specialized sports trend extractor. Output strictly JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content.strip()
            
            # Clean markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            filtered_trends = json.loads(content)
            return filtered_trends
        except Exception as e:
            print(f"❌ LLM Trend Filtering failed: {e}")
            # Dynamic local fallback: extract a simple slice of raw items that mentions football keywords
            fallback = []
            keywords = ["soccer", "football", "world cup", "fifa", "messi", "ronaldo", "mbappe", "goal", "qualifier"]
            for item in raw_items:
                text_lower = item["text"].lower()
                if any(kw in text_lower for kw in keywords):
                    fallback.append({
                        "topic": item["text"][:50],
                        "search_query": item["text"][:30],
                        "trend_score": 50,
                        "reason": f"Heuristic match from {item['source']}"
                    })
                if len(fallback) >= 5:
                    break
            return fallback

if __name__ == "__main__":
    scout = FootballTrendScout()
    trends = scout.get_football_trends()
    print("\n🔥 Top Football Trends Identified:")
    print(json.dumps(trends, indent=4))
