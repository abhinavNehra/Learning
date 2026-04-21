import requests

API_URL = "http://localhost:1234/v1/chat/completions"


prompt = '''Our Node.js API takes 800ms to respond. The DB query takes 50ms. Where is the bottleneck most likely to be?, explain in text no code needed and keep it short'''

for temperature in [0.1, 0.5, 1]:
    response = requests.post(API_URL, json={
        "model": "qwen/qwen3-coder-30b",
        "temperature": temperature,
        "messages": [
          {"role": "system", "content": "You are a senior backend engineer with expertise in performance optimization."},
        {"role": "user", "content": prompt}
      ]
    })

    print('temperature: ', temperature,  " response: ", response.json().get('choices', [{}])[0].get('message', {}).get('content', ''))