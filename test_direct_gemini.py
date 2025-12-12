import google.generativeai as genai
import os

key = "AIzaSyDI8WM1RNCHesHEyC23aSCicWe2_sSRqlk"

print(f"Testing Key: {key[:5]}...")
genai.configure(api_key=key)

with open("model_list.txt", "w", encoding="utf-8") as f:
    f.write("--- Model List ---\n")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"{m.name}\n")
    except Exception as e:
        f.write(f"List Models Failed: {e}\n")

    f.write("\n--- Generation Test ---\n")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello")
        f.write(f"SUCCESS (gemini-1.5-flash): {response.text}\n")
    except Exception as e:
        f.write(f"FAILED (gemini-1.5-flash): {e}\n")
