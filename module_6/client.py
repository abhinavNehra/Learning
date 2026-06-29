import anthropic

client = anthropic.Anthropic(
  base_url = "http://localhost:1234",
  api_key = "lmstudio"
)


def request(max_tokens, temperature, system, messages ):
  return client.messages.create(
        model="qwen/qwen3.6-27b",
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=messages
    )


# result = request("You are a helpful assistant", [{"role": "user", "content": "What is the capital of France?"}])
# print("resut ===", result)