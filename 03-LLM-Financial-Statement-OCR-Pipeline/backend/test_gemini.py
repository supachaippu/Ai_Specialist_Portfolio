import sys
import json
from google import genai
from google.genai import types

def test_gemini():
    try:
        client = genai.Client(api_key="YOUR_GEMINI_API_KEY_HERE")
        prompt = "Hello, what model are you?"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        print("Response:", response.text)
    except Exception as e:
        print("Error:", repr(e))

if __name__ == '__main__':
    test_gemini()
