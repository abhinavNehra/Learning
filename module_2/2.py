import requests

API_URL = "http://localhost:1234/v1/chat/completions"


system = """You are a senior engineer doing async git change reviews at a startup.

The team uses GitHub, React, Node.js, and Postgres. PRs are reviewed by developers 
who did not write the code and have limited time.

When given a git commit id  and description, produce a structured review summary:
1. Identify the change's purpose (what problem does it solve?)
2. Flag any obvious risks (breaking changes, security issues, missing tests)
3. Rate review urgency: blocks-release / needs-discussion / minor / style-only

Respond in this exact format:
PURPOSE: <one sentence>
RISKS: <bullet list, or "None identified">
URGENCY: <one of the four labels above>
QUESTIONS: <up to 3 questions for the author, or "None">

Keep the entire response under 150 words. Be direct — skip filler phrases 
like "It appears that" or "This change seems to"."""

user = f"""Review this git commit :

<title> module 1</title>
<description>this is about module 1 learning</description>
<commitID>75ab21b3e1f2a40f0b609b36f50957f50a971845</commitID>"""


response = requests.post(API_URL, json={
    "model": "qwen/qwen3-coder-30b",
    "temperature": 1,
    "messages": [
      {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]
    })
print('temperature: ', 1,  " response: ", response.json().get('choices', [{}])[0].get('message', {}).get('content', ''))