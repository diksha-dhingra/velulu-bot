import os
from google import genai
from google.genai import types
from personality import SYSTEM_PROMPT

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# In-memory chat sessions — key: sender phone number, value: chat object
chat_sessions: dict = {}


def get_reply(sender: str, user_message: str) -> str:
    if sender not in chat_sessions:
        chat_sessions[sender] = client.chats.create(
            model="gemini-2.0-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )

    chat = chat_sessions[sender]

    try:
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        print(f"Gemini error for {sender}: {e}")
        return "Kuch gadbad ho gayi, thodi der baad try karo."