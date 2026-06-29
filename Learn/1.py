from asyncio.log import logger
import time
from urllib import response

import anthropic
import json

client = anthropic.Anthropic(
    base_url="http://localhost:11434",
    api_key="ollama"
)

# ── Tool implementations ───────────────────────────────────────────

def get_current_weather(city: str) -> str:
    # Real impl: call a weather API here
    return json.dumps({"city": city, "temp_c": 18, "condition": "Partly cloudy"})

def calculate(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # safe for numeric expressions
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def search_web(query: str) -> str:
    # Real impl: call Serper, Tavily, or Brave Search API here
    return json.dumps([
        {"title": f"Search result for '{query}'", "snippet": "Stub result — wire up a real search API."}
    ])

def convert_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9.0 / 5.0) + 32

def get_stock_price(ticker: str) -> str:
    # Return a fake price for now
    prices = {"AAPL": 182.50, "GOOGL": 175.20, "MSFT": 415.00}
    price = prices.get(ticker.upper(), 100.0)
    return json.dumps({"ticker": ticker, "price_usd": price})

# ── Tool registry (maps name → function) ──────────────────────────

TOOL_MAP = {
    "get_current_weather": get_current_weather,
    "calculate":           calculate,
    "search_web":          search_web,
    "convert_to_fahrenheit":  convert_to_fahrenheit,
    "get_stock_price":     get_stock_price,
}

# ── Tool definitions (what the model sees) ─────────────────────────
# These descriptions ARE prompts — write them carefully.

TOOLS = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather for a city. Use when the user asks about weather conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. 'London'"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "Evaluate a mathematical expression. Use for arithmetic, percentages, or any calculation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Python numeric expression, e.g. '1000 / 182.5'"}
            },
            "required": ["expression"]
        }
    },
    {
        "name": "search_web",
        "description": "Search the web for recent information. Use when the user asks about current events or facts you may not have.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "convert_to_fahrenheit",
        "description": "Convert a temperature from Celsius to Fahrenheit.",
        "input_schema": {
            "type": "object",
            "properties": {
                "celsius": {"type": "number", "description": "Temperature in Celsius"}
            },
            "required": ["celsius"]
        }
    },
    {
        "name": "get_stock_price",
        "description": "Get the current stock price for a given ticker symbol. Use when the user asks about stock prices.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. 'AAPL'"}
            },
            "required": ["ticker"]
        }
    }
]

# ── The agent loop ─────────────────────────────────────────────────

def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]


    for i in range(10):
      print('i called ')
      response = client.messages.create(
          model="gemma4:e4b",
          max_tokens=1024,
          tools=TOOLS,
          messages=messages,
      )


      print('respon ---', response.content)

      if response.stop_reason == "end_turn":
          print('stop reason end turn ====>>>', response)
          return response.content[0].text
      # stop_reason == "tool_use" — execute each requested tool

      tool_results = [ tool_execution(block) for block in response.content if block.type == "tool_use" ]
      # tool_results = []
      # for block in response.content:
      #     if block.type != "tool_use":
      #         continue

      #     print(f"→ Calling {block.name}({block.input})")
      #     result = TOOL_MAP[block.name](**block.input)
      #     print(f"← Result: {result}\n")

      #     tool_results.append({
      #         "type": "tool_result",
      #         "tool_use_id": block.id,
      #         "content": result,
      #     })

      # Append both the assistant turn and the tool results to history
      messages.append({"role": "assistant", "content": response.content})
      messages.append({"role": "user",      "content": tool_results})



def tool_execution(block):
    t0 = time.perf_counter()

    try:
      print(f"→ Calling {block.name}({block.input})")
      result = TOOL_MAP[block.name](**block.input)
      latency_ms = int((time.perf_counter() - t0) * 1000)
      print(f"tool={block.name} input={block.input} latency_ms={latency_ms}ms")
        
      print(f"← Result: {result}\n")

      return {
          "type": "tool_result",
          "tool_use_id": block.id,
          "content": result,
      }
    except Exception as e:
      print('Error executing tool:', e)
      return {
          "type": "tool_result",
          "tool_use_id": block.id,
          "is_error": True,
          "content": f"Error executing tool {block.name}: {e}",
      }
    

if __name__ == "__main__":
    answer = run_agent("What's the weather in Tokyo AND London right now, and which city is warmer?")
    print("Final answer:", answer)