#!/usr/bin/env python3

#API AIzaSyBTw-yq0-_4J7W4G2eSnNTRxsrYocfdM1c
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

def get_response(query: str) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=query
    )
    return response.text
