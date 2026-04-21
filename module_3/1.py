import requests

# Few-shot CoT for a code review classifier
# You're teaching it YOUR team's definition of severity

system = """You are a code review classifier. 
When given a code issue, classify its severity by reasoning through it first.
Always reason before classifying."""

# The examples teach the model your specific reasoning pattern
few_shot_examples = [
    {
        "role": "user",
        "content": """Classify this issue:
Issue: Variable declared with 'var' instead of 'const'
Code: var userId = req.params.id"""
    },
    {
        "role": "assistant", 
        "content": """<thinking>
'var' has function scope and can be accidentally redeclared. However, this isn't
a security issue and won't cause a runtime bug in most cases. It's a code quality
issue — it goes against modern JS best practices but doesn't break anything.
The team uses ESLint which would already catch this automatically.
</thinking>
<classification>style</classification>
<reason>Code quality issue caught by linting tools. No runtime risk.</reason>"""
    },
    {
        "role": "user",
        "content": """Classify this issue:
Issue: User input directly interpolated into SQL query
Code: db.query(`SELECT * FROM users WHERE email = req.body.email`)"""
    },
    {
        "role": "assistant",
        "content": """<thinking>
Direct string interpolation of user input into SQL. A malicious user could input:
"' OR '1'='1" and extract all user records, or "'; DROP TABLE users;--"
This is a textbook SQL injection vulnerability. It's not theoretical — it's
trivially exploitable by anyone who knows what they're doing.
This is a production database with real user data.
</thinking>
<classification>critical</classification>
<reason>SQL injection. Trivially exploitable. Blocks merge until fixed.</reason>"""
    }
]

# Now the actual query
new_issue = {
    "role": "user",
    "content": """Classify this issue:
Issue: No rate limiting on login endpoint
Code: app.post('/login', async (req, res) => { /* auth logic */ })"""
}



API_URL = "http://localhost:1234/v1/chat/completions"

response = requests.post(API_URL, json={
    "model": "qwen/qwen3-coder-30b",
    "temperature": 0.1,
    "messages": [
      {"role": "system", "content": system},
        {"role": "user", "content": ','.join([str(example) for example in few_shot_examples + [new_issue]])}
    ]
    })
#print('response ----> ', response.json())
print('temperature: ', 1,  " response: ", response.json().get('choices', [{}])[0].get('message', {}).get('content', ''))