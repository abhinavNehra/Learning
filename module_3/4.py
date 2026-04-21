import requests
import re


API_URL = "http://localhost:1234/v1/chat/completions"

SYSTEM = """You are an expert Python debugger with deep knowledge of common 
runtime errors, async pitfalls, and performance anti-patterns.

When given buggy Python code:
1. Trace through the execution in <thinking></thinking> tags — what actually happens step by step
2. Identify the root cause (not just symptoms)
3. Give the fixed code in <fix></fix> tags
4. Give a one-line explanation in <explanation></explanation> tags

Be precise. The thinking should show your actual reasoning process."""


# /oc
def debug_code(code):
  response = requests.post(API_URL, json={
          "model": "qwen/qwen3-coder-30b",
          "temperature": 0.3,
          "messages": [
            {"role": "system", "content": SYSTEM},
          {"role": "user", "content": code}
    ]
  })

  result = response.json()
  content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
  #print('response ----> ', result)
  #print('content: ', content)
  #print('temperature: ', 0.3,  " response: ", result.get('choices', [{}])[0].get('message', {}).get('content', ''))

  text = content
  # print('Content >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.\n', text)
  # print("=================================================================")

  return {
      "thinking":     re.search(r'<thinking>(.*?)</thinking>',     text, re.DOTALL).group(1).strip(),
      "fix":          re.search(r'<fix>(.*?)</fix>',               text, re.DOTALL).group(1).strip(),
      "explanation":  re.search(r'<explanation>(.*?)</explanation>', text, re.DOTALL).group(1).strip(),
      "tokens_used":  result.get('usage', {}).get('prompt_tokens', 0) + result.get('usage', {}).get('completion_tokens', 0)
  }



bugs = [
    # Bug 1: Classic mutable default argument
    """def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item("a"))
print(add_item("b"))  # Expected: ["b"], Got: ["a", "b"]""",

    # Bug 2: Missing await (your bread and butter as a Node dev moving to Python)
    """import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return {"data": 42}

async def main():
    result = fetch_data()   # forgot await
    print(result["data"])   # crashes

asyncio.run(main())""",

    # Bug 3: Subtle off-by-one with slicing
    """def get_last_n(items, n):
    return items[-n:]   # seems right...

items = [1, 2, 3, 4, 5]
print(get_last_n(items, 0))  # Expected: [], Got: [1,2,3,4,5]"""
]

for i, bug in enumerate(bugs, 1):
    print(f"\n{'='*50}")
    print(f"BUG {i}")
    print(f"{'='*50}")
    result = debug_code(bug)
    print(f"\nREASONING:\n{result['thinking']}")
    print(f"\nFIX:\n{result['fix']}")
    print(f"\nEXPLANATION: {result['explanation']}")
    print(f"Tokens used: {result['tokens_used']}")