# FILE: src/llama_client.py

import requests
import json

def call_llama(prompt, model="llama3:8b"):
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt}

    response = requests.post(url, json=payload, stream=True)
    full_output = ""

    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            if "response" in data:
                full_output += data["response"]

    return full_output
