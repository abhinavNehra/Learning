# Lesson 1 Practiced — Agent Built with Ollama

Abhinav wrote `Learn/1.py` independently after Lesson 1. He adapted the agent loop to run against a local Ollama model (gemma4:e4b at localhost:11434) instead of the Anthropic API — showing cost awareness and practical initiative. He added a 5th tool (`convert_to_fahrenheit`) beyond what the exercise asked for, and extracted `tool_execution` into its own function with proper error handling (`is_error: True`) matching the Production Hardening section.

**Evidence:** `Learn/1.py` — full agent loop, 5 tools, Ollama backend, `for i in range(10)` as the max iterations guard, `tool_execution()` helper.

**Implications:** He is actively applying the lessons, not just reading them. Future lessons should reference his own code as examples ("your `Learn/1.py` already does this — now extend it"). He has Ollama set up locally, which means Lesson 2 can use a local embedding model for RAG instead of requiring an API.
