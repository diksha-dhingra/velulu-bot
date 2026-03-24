import os
from groq import Groq
from personality import SYSTEM_PROMPT

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# In-memory chat history — key: sender phone number, value: list of messages
chat_sessions: dict = {}


def get_reply(sender: str, user_message: str) -> str:
    if sender not in chat_sessions:
        chat_sessions[sender] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    chat_sessions[sender].append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_sessions[sender]
        )
        reply = response.choices[0].message.content
        chat_sessions[sender].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        print(f"Groq error for {sender}: {e}")
        return "Kuch gadbad ho gayi, thodi der baad try karo."