import re
import requests
import threading
from utils import send_whatsapp_message
from personality import HELP_MESSAGE, ABOUT_MESSAGE, WELCOME_MESSAGE

# Per-user to-do lists
todo_lists: dict = {}

def is_command(message: str) -> bool:
    msg = message.strip().lower()
    for cmd in ["/song", "/weather", "/add", "/done", "/remind", "/timer"]:
        if msg.startswith(cmd):
            return True
        if msg.startswith("/remove"):
            return True
    return msg in ["/help", "/reset", "/about", "/start", "/joke", "/mytasks"]


def handle_command(message: str, sender: str, chat_sessions: dict) -> str:
    msg = message.strip()
    cmd = msg.lower().split()[0] if msg else ""

    if cmd == "/start":
        return WELCOME_MESSAGE
    elif cmd == "/help":
        return HELP_MESSAGE
    elif cmd == "/reset":
        if sender in chat_sessions:
            del chat_sessions[sender]
        return "Chat reset! Fresh start 👍"
    elif cmd == "/about":
        return ABOUT_MESSAGE
    elif cmd == "/joke":
        return get_joke()
    elif cmd == "/weather":
        city = msg[8:].strip()
        if not city:
            return "City batao! `/weather Delhi`"
        return get_weather(city)
    elif cmd == "/add":
        task = msg[4:].strip()
        if not task:
            return "Task likho! `/add buy milk`"
        return add_task(sender, task)
    elif cmd == "/mytasks":
        return get_tasks(sender)
    elif cmd == "/done":
        try:
            num = int(msg.split()[1]) - 1
            return complete_task(sender, num)
        except:
            return "Enter task number! `/done 1`"
    elif cmd == "/remove":
        try:
            num = int(msg.split()[1]) - 1
            return remove_task(sender, num)
        except:
            return "Enter task number! `/remove 1`"
    elif cmd == "/remind":
        return set_reminder(sender, msg[7:].strip())
    elif cmd == "/timer":
        return set_timer(sender, msg[6:].strip())
    elif cmd == "/song":
        query = msg[5:].strip()
        if not query:
            return "Song name likho! `/song tum hi ho`"
        return search_song(query)

    return "Unknown command. Type /help"


# ── Joke ──────────────────────────────────────────────────────────────────────
def get_joke() -> str:
    try:
        r = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode&type=single", timeout=5)
        if r.status_code == 200:
            return f"😄 {r.json().get('joke', '')}"
    except:
        pass
    return "My joke database is on a coffee break 😅 Try again!"


# ── Weather ───────────────────────────────────────────────────────────────────
def get_weather(city: str) -> str:
    try:
        r = requests.get(f"https://wttr.in/{city}?format=4", timeout=5)
        if r.status_code == 200:
            return f"🌤 {r.text.strip()}"
    except:
        pass
    return "Couldn't fetch weather. Check city name!"


# ── To-do List ────────────────────────────────────────────────────────────────
def add_task(sender: str, task: str) -> str:
    if sender not in todo_lists:
        todo_lists[sender] = []
    todo_lists[sender].append({"task": task, "done": False})
    num = len(todo_lists[sender])
    return f"✅ Task {num} added: {task}"


def get_tasks(sender: str) -> str:
    tasks = todo_lists.get(sender, [])
    if not tasks:
        return "No tasks! Add one with `/add buy milk`"
    lines = ["📋 Your Tasks:\n"]
    for i, t in enumerate(tasks, 1):
        status = "✅" if t["done"] else "⬜"
        lines.append(f"{status} {i}. {t['task']}")
    return "\n".join(lines)


def complete_task(sender: str, index: int) -> str:
    tasks = todo_lists.get(sender, [])
    if not tasks or index < 0 or index >= len(tasks):
        return "Invalid task number!"
    tasks[index]["done"] = True
    return f"✅ Done: {tasks[index]['task']}"

def remove_task(sender: str, index: int) -> str:
    tasks = todo_lists.get(sender, [])
    if not tasks or index < 0 or index >= len(tasks):
        return "Invalid task number!"
    removed = tasks.pop(index)
    return f"🗑 Removed: {removed['task']}"



# ── Time Parser ───────────────────────────────────────────────────────────────
def parse_time(text: str):
    match = re.search(r'(\d+)\s*(sec|min|hr|hour|s|m|h)', text.lower())
    if not match:
        return None, None
    value = int(match.group(1))
    unit = match.group(2)
    if unit in ["sec", "s"]:
        return value, f"{value} seconds"
    elif unit in ["min", "m"]:
        return value * 60, f"{value} minutes"
    else:
        return value * 3600, f"{value} hours"


# ── Reminder ──────────────────────────────────────────────────────────────────
def set_reminder(sender: str, text: str) -> str:
    seconds, label = parse_time(text)
    if not seconds:
        return "Format: `/remind 30min call mom`"

    reminder_msg = re.sub(r'\d+\s*(sec|min|hr|hour|s|m|h)', '', text, flags=re.IGNORECASE).strip()
    if not reminder_msg:
        reminder_msg = "Your reminder!"

    def fire():
        send_whatsapp_message(sender, f"⏰ Reminder: {reminder_msg}")

    threading.Timer(seconds, fire).start()
    return f"⏰ Reminder set for {label}!"


# ── Timer ─────────────────────────────────────────────────────────────────────
def set_timer(sender: str, text: str) -> str:
    seconds, label = parse_time(text)
    if not seconds:
        return "Format: `/timer 10min`"

    def fire():
        send_whatsapp_message(sender, f"⏰ Timer done! Your {label} timer is up!")

    threading.Timer(seconds, fire).start()
    return f"⏰ Timer started for {label}!"


# ── Song ──────────────────────────────────────────────────────────────────────
def search_song(query: str) -> str:
    youtube_url = search_youtube(query)
    spotify_result = search_spotify(query)

    if not spotify_result and not youtube_url:
        return f"Couldn't find *{query}*. Try with more details!"

    reply = "🎵 *Song Found!*\n\n"
    if spotify_result:
        name, artist, spotify_url = spotify_result
        reply += f"🎤 *{name}* — {artist}\n\n"
        reply += f"🟢 Spotify: {spotify_url}\n"
    else:
        reply += f"🔍 *{query}*\n\n❌ Not available on Spotify\n"

    if youtube_url:
        reply += f"▶️ YouTube: {youtube_url}"
    else:
        reply += "❌ YouTube video not found"

    return reply


def search_youtube(query: str) -> str:
    try:
        import os
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        results = tavily.search(query=f"{query} lyrics video site:youtube.com", max_results=1)
        for r in results.get("results", []):
            url = r.get("url", "")
            if "youtube.com/watch" in url or "youtu.be" in url:
                return url
    except Exception as e:
        print(f"YouTube search error: {e}")
    return None


def search_spotify(query: str):
    import os, base64
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None
    try:
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {credentials}"},
            data={"grant_type": "client_credentials"}
        )
        token = r.json().get("access_token")
        r2 = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": query, "type": "track", "limit": 1}
        )
        tracks = r2.json().get("tracks", {}).get("items", [])
        if tracks:
            t = tracks[0]
            return t["name"], t["artists"][0]["name"], t["external_urls"]["spotify"]
    except Exception as e:
        print(f"Spotify error: {e}")
    return None