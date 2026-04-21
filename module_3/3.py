import requests

API_URL = "http://localhost:1234/v1/chat/completions"


system = """You are a helpful assistant for a legal tech platform.

Before answering any question, reason through it carefully inside <thinking> tags.
Consider: accuracy, potential misinterpretation, and whether you need more context.
After reasoning, give your final response inside <answer> tags.

The user only sees what is inside <answer> tags."""

user_message = "Can I fire someone for posting on social media?"
response = requests.post(API_URL, json={
    "model": "qwen/qwen3-coder-30b",
    "temperature": 0.3,
    "messages": [
      {"role": "system", "content": system},
    {"role": "user", "content": user_message}
  ]
})

print('temperature: ', 0.3,  " response: ", response.json().get('choices', [{}])[0].get('message', {}).get('content', ''))