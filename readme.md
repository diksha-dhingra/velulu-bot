# 🤖 Sparky — AI WhatsApp Assistant

A smart, friendly WhatsApp bot powered by **Groq (LLaMA 3.3 70B)** with live web search, music discovery, reminders, to-do lists, and more!

> Created by **Diksha Dhingra**

---

## ✨ Features

- 🧠 **AI Chat** — Powered by Groq LLaMA 3.3 70B with multi-model rotation
- 🔍 **Live Web Search** — Real-time results via Tavily (IPL scores, news, crypto prices)
- 🎵 **Music Discovery** — Spotify & YouTube links for any song
- ⏰ **Reminders & Timers** — Get pinged on WhatsApp when time is up
- 📋 **To-Do List** — Add, view, complete, and remove tasks
- 🌤 **Weather** — Live weather for any city
- 😄 **Jokes** — Random jokes on demand
- 💬 **20-message memory** — Sparky remembers your conversation context

---

## 🗂 Project Structure

```
Sparky-Bot/
├── main.py          # Flask app, webhook handling
├── bot.py           # Groq AI integration, model rotation
├── commands.py      # All bot commands logic
├── personality.py   # Bot name, personality, messages
├── utils.py         # WhatsApp message sender
├── requirements.txt # Dependencies
├── Procfile         # Railway deployment config
└── .gitignore       # Ignored files
```

---

## ⚙️ Setup & Deployment

### 1. Clone the repo
```bash
git clone https://github.com/diksha-dhingra/Sparky-Bot
cd Sparky-Bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file:
```env
WHATSAPP_TOKEN=your_whatsapp_token
PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_verify_token
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

### 4. Deploy on Railway
- Push code to GitHub
- Connect repo on [railway.app](https://railway.app)
- Add all environment variables
- Deploy!

### 5. Set Webhook on Meta
- Go to [developers.facebook.com](https://developers.facebook.com)
- WhatsApp → Configuration → Webhook URL:
```
https://your-railway-url.railway.app/webhook
```

---

## 💬 Commands

| Command | Description |
|---|---|
| `/start` | Welcome message |
| `/help` | Show all commands |
| `/about` | About Sparky |
| `/reset` | Clear conversation |
| `/joke` | Random joke 😄 |
| `/weather [city]` | Live weather update 🌤 |
| `/song [name]` | Spotify + YouTube links 🎵 |
| `/add [task]` | Add a to-do task 📋 |
| `/mytasks` | View your tasks |
| `/done [number]` | Mark task as complete ✅ |
| `/remove [number]` | Remove a task 🗑 |
| `/remind [time] [msg]` | Set a reminder ⏰ |
| `/timer [time]` | Set a countdown timer ⏰ |

---

## 🔑 APIs Used

| API | Purpose | Free Tier |
|---|---|---|
| [Groq](https://groq.com) | AI responses | 100k tokens/day |
| [Tavily](https://tavily.com) | Web search | 1000 searches/month |
| [Spotify](https://developer.spotify.com) | Song search | Free |
| [Meta WhatsApp](https://developers.facebook.com) | Messaging | Free |
| [wttr.in](https://wttr.in) | Weather | Free |
| [JokeAPI](https://v2.jokeapi.dev) | Jokes | Free |

---

## 🛡 Uptime Monitoring

Bot is monitored 24/7 via [UptimeRobot](https://uptimerobot.com) — pings every 5 minutes to keep Railway from sleeping.

Health check endpoint: `GET /` → `Sparky is alive! 🚀`

---

## 📝 License

MIT License — feel free to fork and build your own version!

---

<p align="center">Made with ❤️ by Diksha Dhingra</p>