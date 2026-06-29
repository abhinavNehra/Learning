# eval_framework.py
# Run this before shipping any prompt change

#import anthropic
import json
import asyncio
import sys
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

# Handle both direct execution and module imports
try:
    from .client import request
except (ImportError, ValueError):
    # Fallback for direct script execution
    sys.path.insert(0, str(Path(__file__).parent))
    from client import request

#client = anthropic.Anthropic()

# ── Data structures ──────────────────────────────────────────

@dataclass
class TestCase:
    id:            str
    input:         str
    expected:      str | None = None      # None for open-ended tasks
    must_include:  list[str]  = field(default_factory=list)
    must_exclude:  list[str]  = field(default_factory=list)
    category:      str        = "general" # happy_path | edge_case | failure

@dataclass
class EvalResult:
    case_id:       str
    prompt_id:     str
    output:        str
    scores:        dict       # {"accuracy": 8, "completeness": 7, ...}
    passed:        bool
    failure_reason: str | None = None

# ── Scoring functions ────────────────────────────────────────

def score_exact(output: str, expected: str) -> float:
    return 1.0 if output.strip().lower() == expected.strip().lower() else 0.0

def score_contains(output: str, must_include: list, must_exclude: list) -> float:
    if not must_include and not must_exclude:
        return 1.0
    include_score = (
        sum(1 for item in must_include if item.lower() in output.lower())
        / len(must_include)
        if must_include else 1.0
    )
    exclude_score = (
        sum(1 for item in must_exclude if item.lower() not in output.lower())
        / len(must_exclude)
        if must_exclude else 1.0
    )
    return (include_score + exclude_score) / 2

def score_json_valid(output: str) -> float:
    try:
        json.loads(output)
        return 1.0
    except json.JSONDecodeError:
        return 0.0

def score_with_rubric(question: str, output: str, rubric: str) -> dict:
    """LLM-as-judge rubric scoring."""
    result = request(
        max_tokens=200,
          temperature=0,
            system=f"""You are an objective evaluator. Score the response below using this rubric:

{rubric}

Return ONLY valid JSON with numeric scores. No explanation outside the JSON.""",
        messages=[{
            "role": "user",
            "content": f"Question: {question}\n\nResponse to score:\n{output}"
        }])
    
    
    try:
        return json.loads(result.content[0].text)
    except json.JSONDecodeError:
        return {"error": "judge_failed"}

# ── LLM-as-judge: pairwise comparison ───────────────────────

def llm_judge_pairwise(
    question:   str,
    response_a: str,
    response_b: str,
    criteria:   str = "accuracy, helpfulness, and conciseness"
) -> dict:
    """
    Ask judge twice with A/B swapped — cancels position bias.
    Models tend to prefer whichever response they see first.
    """
    def judge(q, r1, r2, label_1, label_2):
        result =  request(
            max_tokens=200,
            temperature=0,
            system=f"""Compare two AI responses to the same question.
            Judge only on: {criteria}.
            Return JSON: {{"winner": "{label_1}" | "{label_2}" | "tie", "reason": "one sentence"}}""",
            messages=[{"role": "user", "content":
                f"Question: {q}\n\n"
                f"Response {label_1}:\n{r1}\n\n"
                f"Response {label_2}:\n{r2}"}]
        )
        
        return json.loads(result.content[0].text)

    # Run twice with positions swapped
    result_1 = judge(question, response_a, response_b, "A", "B")
    result_2 = judge(question, response_b, response_a, "B", "A")

    # Normalise: in result_2, "B" means response_a won
    winner_1 = result_1["winner"]
    raw_2    = result_2["winner"]
    winner_2 = "A" if raw_2 == "B" else ("B" if raw_2 == "A" else "tie")

    # Both runs agree → confident result
    if winner_1 == winner_2:
        return {"winner": winner_1, "confidence": "high", "reason": result_1["reason"]}

    # Runs disagree → call it a tie
    return {"winner": "tie", "confidence": "low", "reason": "judges disagreed"}

# ── Main eval runner ─────────────────────────────────────────

def run_eval(
    prompt_fn:  Callable[[str], str],   # your prompt function: input → output
    test_cases: list[TestCase],
    rubric:     str | None = None,
    prompt_id:  str        = "v1"
) -> list[EvalResult]:
    results = []

    print('prompt id :', prompt_id)

    for case in test_cases:

        print('case   ----', case)

        output = prompt_fn(case.input)

        # Score 1 — contains check (always run)
        contains_score = score_contains(output, case.must_include, case.must_exclude)

        # Score 2 — exact match (if expected provided)
        exact_score = (
            score_exact(output, case.expected)
            if case.expected else None
        )

        # Score 3 — rubric (if rubric provided)
        rubric_scores = (
            score_with_rubric(case.input, output, rubric)
            if rubric else {}
        )

        # Determine pass/fail
        passed        = contains_score >= 0.8
        failure_reason = None
        if not passed:
            missing = [i for i in case.must_include if i.lower() not in output.lower()]
            present = [e for e in case.must_exclude if e.lower() in output.lower()]
            failure_reason = f"Missing: {missing}. Should not contain: {present}"

        results.append(EvalResult(
            case_id        = case.id,
            prompt_id      = prompt_id,
            output         = output,
            scores         = {"contains": contains_score, "exact": exact_score, **rubric_scores},
            passed         = passed,
            failure_reason = failure_reason
        ))

    return results

# ── Reporting ────────────────────────────────────────────────

def print_report(results_a: list[EvalResult], results_b: list[EvalResult] | None = None):
    def summarise(results, label):
        total    = len(results)
        passed   = sum(1 for r in results if r.passed)
        pass_rate = passed / total * 100
        avg_contains = sum(r.scores.get("contains", 0) for r in results) / total

        print(f"\n{'─'*40}")
        print(f"  {label}")
        print(f"{'─'*40}")
        print(f"  Pass rate:     {pass_rate:.1f}% ({passed}/{total})")
        print(f"  Avg contains:  {avg_contains:.2f}")

        # Show failures
        failures = [r for r in results if not r.passed]
        if failures:
            print(f"\n  Failures ({len(failures)}):")
            for f in failures:
                print(f"  ✗ [{f.case_id}] {f.failure_reason}")

        return pass_rate

    rate_a = summarise(results_a, "Prompt A")
    if results_b:
        rate_b = summarise(results_b, "Prompt B")
        delta  = rate_b - rate_a
        print(f"\n  {'→ SHIP B' if delta > 5 else '→ KEEP A' if delta < -5 else '→ TOO CLOSE — need more cases'}")
        print(f"  Delta: {delta:+.1f}%")