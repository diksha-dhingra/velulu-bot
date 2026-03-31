import os
from groq import Groq
from personality import SYSTEM_PROMPT

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chat_sessions: dict = {}

def get_reply(sender: str, user_message: str) -> str:
    if sender not in chat_sessions:
        chat_sessions[sender] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    chat_sessions[sender].append({"role": "user", "content": user_message})

    if len(chat_sessions[sender]) > 51:
        chat_sessions[sender] = [chat_sessions[sender][0]] + chat_sessions[sender][-50:]

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