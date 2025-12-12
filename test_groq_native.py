import os
from groq import Groq

os.environ["GROQ_API_KEY"] = "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"

try:
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain what 1+1 is",
            }
        ],
        model="llama3-70b-8192",
    )

    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
