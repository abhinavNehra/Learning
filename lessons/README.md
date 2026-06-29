# Lessons

[← Back to Book](../README.md)

---

## Phase 1 — AI Builder

*Using models expertly. Building real systems, not API toys.*

---

### Lesson 1: AI Agents & Tool Use

**Status:** ✓ Complete  
**Time:** 75 min  
**Practice code:** [`Learn/1.py`](../Learn/1.py)

The first real step beyond prompt engineering. You built an agent that decides when to
call tools vs answer directly, handled parallel tool calls, and learned the four guards
every production agent needs.

**What you learned:**
- The perceive → decide → act → observe loop (ReAct pattern)
- Tool definitions: name, description, input_schema
- Parallel tool calls — one response, multiple `tool_use` blocks
- Production hardening: max iterations, token budget, `is_error: True`, logging
- Three agent architectures: ReAct, Plan-and-Execute, Reflection
- Four memory types: in-context, vector DB, structured DB, episodic
- Six interview-ready answers

**[Open Lesson →](0001-ai-agents-tool-use.html)**

---

### Lesson 2: RAG Pipelines

**Status:** Upcoming

Build a real document search system: chunk documents, embed them, store in a vector DB,
and retrieve semantically relevant chunks at query time. This is the most common AI
pattern in production after agents.

**What you will learn:**
- Chunking strategy (size, overlap, why it matters)
- Embeddings: what they are, how to generate them
- Vector DBs: pgvector (Postgres), Chroma (local), Pinecone (cloud)
- The RAG prompt pattern: grounding answers in retrieved context
- Retrieval quality: similarity thresholds, reranking, top-k selection

*Coming in next session.*

---

### Lesson 3: Production AI Patterns

**Status:** Upcoming

The gap between "it works on my machine" and "it works at scale." Streaming responses,
retry logic, cost control, rate limiting, and caching patterns for AI APIs.

---

### Lesson 4: Multi-modal AI

**Status:** Upcoming

Text is one modality. Modern models see images too. Learn to send images to Claude,
extract structured data from screenshots, and build pipelines that combine vision and text.

---

### Lesson 5: AI Evals in Production

**Status:** Upcoming

You built an eval framework in Module 6. This lesson goes further: automated regression
testing, LLM-as-judge pairwise comparison, and building a CI pipeline that blocks prompt
regressions before they reach users.

---

## Phase 2 — Model Whisperer

*Understanding how models actually work. The knowledge behind the tool.*

Locked until Phase 1 is complete.

| Lesson | Topic |
|--------|-------|
| 2.1 | Transformers from first principles |
| 2.2 | The attention mechanism — visual walkthrough |
| 2.3 | Modern architectures: GPT, LLaMA, Mistral |
| 2.4 | Build a tiny GPT from scratch (Karpathy-style) |

---

## Phase 3 — Model Modifier

*Changing what a model knows and how it behaves.*

Locked until Phase 2 is complete.

| Lesson | Topic |
|--------|-------|
| 3.1 | Fine-tuning basics: when and why |
| 3.2 | LoRA and PEFT — efficient fine-tuning |
| 3.3 | Instruction tuning your own model |
| 3.4 | RLHF concepts: reward models and preference data |

---

## Phase 4 — Production AI

*Serving models at scale.*

Locked until Phase 3 is complete.

| Lesson | Topic |
|--------|-------|
| 4.1 | Model serving with vLLM |
| 4.2 | Docker + CUDA — packaging GPU workloads |
| 4.3 | Cloud deployment: AWS / GCP / Azure |
| 4.4 | Monitoring AI in production |

---

## Phase 5 — Expert

*Staying current in a field that rewrites itself every six months.*

Locked until Phase 4 is complete.

| Lesson | Topic |
|--------|-------|
| 5.1 | Reading AI research papers without a PhD |
| 5.2 | Multi-agent systems and coordination patterns |
| 5.3 | AI safety and alignment — what engineers need to know |
| 5.4 | Building your personal system for staying current |

---

## Your Practice Code

All code you write after each lesson lives in `Learn/`:

| File | Lesson | What it does |
|------|--------|--------------|
| [`Learn/1.py`](../Learn/1.py) | Lesson 1 | Agent with 5 tools, Ollama local model, production loop |

---

*Each lesson unlocks the next. Take them in order — every phase assumes the one before.*

[← Back to Book](../README.md)
