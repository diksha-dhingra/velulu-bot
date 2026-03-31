import os
import requests
import base64
from personality import HELP_MESSAGE, ABOUT_MESSAGE, WELCOME_MESSAGE

COMMANDS = ["/help", "/reset", "/about", "/start", "/song"]


def is_command(message: str) -> bool:
    msg = message.strip().lower()
    return msg in COMMANDS or msg.startswith("/song")


def handle_command(message: str, sender: str, chat_sessions: dict) -> str:
    cmd = message.strip().lower()

    if cmd == "/start":
        return WELCOME_MESSAGE

    elif cmd == "/help":
        return HELP_MESSAGE

    elif cmd == "/reset":
        if sender in chat_sessions:
            del chat_sessions[sender]
        return "🔄 Conversation cleared! Let's start fresh. What's on your mind?"

    elif cmd == "/about":
        return ABOUT_MESSAGE

    elif cmd.startswith("/song"):
        query = message.strip()[5:].strip()
        if not query:
            return "🎵 Kuch toh likho! `/song tere naam` ya `/song arijit singh tum hi ho`"
        return search_song(query)

    return "❓ Unknown command. Type */help* to see available commands."


def get_spotify_token() -> str:
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {credentials}"},
        data={"grant_type": "client_credentials"}
    )

    if response.status_code == 200:
        return response.json().get("access_token")
    return None


def search_spotify(query: str):
    token = get_spotify_token()
    if not token:
        return None

    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": query, "type": "track", "limit": 1}
    )

    if response.status_code == 200:
        tracks = response.json().get("tracks", {}).get("items", [])
        if tracks:
            track = tracks[0]
            name = track["name"]
            artist = track["artists"][0]["name"]
            spotify_url = track["external_urls"]["spotify"]
            return name, artist, spotify_url
    return None


def search_youtube(query: str) -> str:
    try:
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        results = tavily.search(
            query=f"{query} lyrics video site:youtube.com",
            max_results=1
        )
        for r in results.get("results", []):
            url = r.get("url", "")
            if "youtube.com/watch" in url or "youtu.be" in url:
                return url
    except Exception as e:
        print(f"YouTube search error: {e}")
    return None


def search_song(query: str) -> str:
    # Spotify search
    spotify_result = search_spotify(query)

    # YouTube search
    youtube_url = search_youtube(query)

    if not spotify_result and not youtube_url:
        return f"😕 Couldn't find *{query}*. Try with more details like singer name or full title!"

    reply = "🎵 *Song Found!*\n\n"

    if spotify_result:
        name, artist, spotify_url = spotify_result
        reply += f"🎤 *{name}* — {artist}\n\n"
        reply += f"🟢 *Spotify:* {spotify_url}\n"
    else:
        reply += f"🔍 *{query}*\n\n"
        reply += "❌ *Spotify:* Not available on Spotify\n"

    if youtube_url:
        reply += f"▶️ *YouTube:* {youtube_url}"
    else:
        reply += "❌ *YouTube:* Video not found"

    return reply