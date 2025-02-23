#!/usr/bin/env python3

#API AIzaSyBTw-yq0-_4J7W4G2eSnNTRxsrYocfdM1c
from google import genai

def get_response(query: str) -> str:
    client = genai.Client(api_key="AIzaSyBTw-yq0-_4J7W4G2eSnNTRxsrYocfdM1c")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=query
    )
    return response.text
