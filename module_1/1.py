import requests

API_URL = "http://localhost:1234/v1/chat/completions"

prompt = "Write a one-sentence description of what React is."



for temp in [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]:
    response = requests.post(API_URL, json={
    "model": "qwen/qwen3-coder-30b",
    "temperature": temp,
    "messages": [
      { "role": "user", "content": prompt }
    ]
    })
    print('temperature: ', temp,  " response: ", response.json().get('choices', [{}])[0].get('message', {}).get('content', ''))
