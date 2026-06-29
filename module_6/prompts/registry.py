# prompts/registry.py
# Single source of truth for all prompt versions

import sys
from pathlib import Path

# Handle both direct execution and module imports
try:
    from ..client import request
    from ..eval_framework import run_eval
    from ..ab_test import TEST_CASES
except (ImportError, ValueError):
    # Fallback for direct script execution
    parent = Path(__file__).parent.parent
    sys.path.insert(0, str(parent))
    from client import request
    from eval_framework import run_eval
    from ab_test import TEST_CASES


print('--------------------------PROMPT REGISTRY--------------------------')
PROMPT_REGISTRY = {
    "support_bot": {
        "v1.0": {
            "released":    "2024-01-15",
            "pass_rate":   0.74,
            "description": "Initial version",
            "system":      "You are Abhi, a senior developer..."
        },
        "v1.1": {
            "released":    "2024-02-03",
            "pass_rate":   0.81,
            "description": "Added CoT for debugging, tighter format rules",
            "system":      "You are Abhi... Think step by step..."
        },
        "v1.2": {
            "released":    None,          # not shipped yet
            "pass_rate":   None,          # not evaluated yet
            "description": "Testing: XML output tags for structured parsing",
            "system":      "You are Abhi... Use <thinking> and <answer> tags..."
        },
        "current": "v1.1"                 # what's in production
    }
}

def get_prompt(name: str, version: str = "current") -> str:
    reg  = PROMPT_REGISTRY[name]
    ver  = reg["current"] if version == "current" else version
    return reg[ver]["system"]

# ── Regression test — run before every deploy ────────────────

def regression_test(prompt_name: str, new_version: str) -> bool:
    """
    New version must pass at least as many cases as current production.
    Prevents shipping a 'better' prompt that broke known good cases.
    """
    current  = get_prompt(prompt_name, "current")
    proposed = get_prompt(prompt_name, new_version)

    def run_prompt(system):
        return lambda inp: request(
            max_tokens=512, temperature=0,
            system=system,
            messages=[{"role": "user", "content": inp}]
        ).content[0].text

    print('current ----', current)
    print('proposed ---', proposed)
    results_current  = run_eval(run_prompt(current),  TEST_CASES, prompt_id="current")
    results_proposed = run_eval(run_prompt(proposed), TEST_CASES, prompt_id=new_version)

    print('checking')
    current_pass  = sum(1 for r in results_current  if r.passed)
    proposed_pass = sum(1 for r in results_proposed if r.passed)

    if proposed_pass < current_pass:
        failures = [r for r in results_proposed if not r.passed]
        regressions = [
            r for r in failures
            if any(rc.case_id == r.case_id and rc.passed for rc in results_current)
        ]
        print(f"❌ REGRESSION: {len(regressions)} cases that used to pass now fail:")
        for r in regressions:
            print(f"   [{r.case_id}] {r.failure_reason}")
        return False

    print(f"✅ No regression. {proposed_pass}/{len(TEST_CASES)} pass "
          f"(was {current_pass}/{len(TEST_CASES)})")
    return 


regression_test("support_bot", "v1.0")