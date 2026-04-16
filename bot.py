import os
from groq import Groq
from tavily import TavilyClient
from personality import SYSTEM_PROMPT

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

chat_sessions: dict = {}

# Keywords jab web search karni ho
SEARCH_TRIGGERS = [
    "score", "live", "news", "today", "latest", "current", "price",
    "weather", "match", "result", "update", "winner", "ipl", "cricket",
    "stock", "rate", "happening", "right now", "aaj", "abhi", "kya hua",
    "who won", "kaun jeeta", "crypto", "bitcoin", "breaking"
]

def needs_search(message: str) -> bool:
    message_lower = message.lower()
    return any(trigger in message_lower for trigger in SEARCH_TRIGGERS)

def search_web(query: str) -> str:
    try:
        result = tavily.search(
            query=query,
            search_depth="basic",
            max_results=3
        )
        snippets = []
        for r in result.get("results", []):
            snippets.append(f"- {r['title']}: {r['content'][:200]}")
        
        if snippets:
            return "Web search results:\n" + "\n".join(snippets)
        return ""
    except Exception as e:
        print(f"Tavily error: {e}")
        return ""

def get_reply(sender: str, user_message: str) -> str:
    if sender not in chat_sessions:
        chat_sessions[sender] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Web search agar zaroorat ho
    search_context = ""
    if needs_search(user_message):
        print(f"Searching web for: {user_message}")
        search_context = search_web(user_message)

    # Search results ko message ke saath bhejo
    if search_context:
        enriched_message = f"{user_message}\n\n[Live Web Data]:\n{search_context}\n\nAnswer using this fresh data. Be accurate and concise."
    else:
        enriched_message = user_message

    chat_sessions[sender].append({"role": "user", "content": enriched_message})

    if len(chat_sessions[sender]) > 21:
        chat_sessions[sender] = [chat_sessions[sender][0]] + chat_sessions[sender][-20:]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_sessions[sender],
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9
        )
        reply = response.choices[0].message.content.strip()
        chat_sessions[sender].append({"role": "assistant", "content": reply})
        return reply

    except Exception as e:
        print(f"Groq error for {sender}: {e}")
        return "⚠️ Something went wrong. Please try again in a moment!"