#!/usr/bin/env python3
"""Run the scenarios of tests/*.md through the Claude CLI and grade them.

Each scenario runs in a fresh temporary workspace outside the repository, holding a copy
of the skills (in .claude/skills/) and of tests/data/. Two checks are made:

- trigger: the skills loaded by the agent (Skill tool calls, or reads of a SKILL.md) are
  compared with the "Expected skill" line of the scenario;
- grading: unless --no-grade, a separate Claude session reads the transcript and the
  workspace and grades each checklist item and the expected result.

Only the Python standard library and the `claude` CLI are needed. The idea of LLM-graded
assertions in an isolated session comes from https://github.com/dekart-xyz/geosql.
"""

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
SKILLS = REPO / "skills"

AGENT_TOOLS = [
    "Skill", "Read", "Write", "Edit", "Glob", "Grep",
    "Bash(curl:*)", "Bash(jq:*)", "Bash(python3:*)", "Bash(mkdir:*)", "Bash(ls:*)",
    "Bash(cat:*)", "Bash(head:*)", "Bash(printf:*)", "Bash(wc:*)",
    "Bash(ogr2ogr:*)", "Bash(ogrinfo:*)", "Bash(gdal:*)", "Bash(gdalinfo:*)",
    "Bash(gdalwarp:*)", "Bash(gdal_translate:*)", "Bash(gdalbuildvrt:*)",
    "Bash(gdaldem:*)", "Bash(gdaltransform:*)", "Bash(gdallocationinfo:*)",
    "Bash(gdalsrsinfo:*)", "Bash(cs2cs:*)", "Bash(projinfo:*)",
]
GRADER_TOOLS = ["Read", "Glob", "Grep", "Bash(gdalinfo:*)", "Bash(ogrinfo:*)",
                "Bash(ls:*)", "Bash(head:*)", "Bash(wc:*)"]


# --- Scenario parsing -----------------------------------------------------------

def parse_expected_skills(paragraph, known):
    """Return (required, forbidden, optional) from an "Expected skill" paragraph."""
    text = " ".join(paragraph.split())
    required, forbidden = None, []
    for match in re.finditer(r"`([a-z0-9-]+)`", text):
        name = match.group(1)
        if name not in known:
            continue
        if text[:match.start()].rstrip().lower().endswith("not"):
            forbidden.append(name)
        elif required is None:
            required = name
    return required, forbidden, "(optional" in text


def parse_scenarios(path, known):
    cases = []
    for section in re.split(r"(?m)^(?=## )", path.read_text(encoding="utf-8")):
        header = re.match(r"## ([A-Z]+-[A-Z0-9]+)\s+—\s+(.*)", section)
        if not header:
            continue
        lines = section.splitlines()
        prompt = " ".join(line[2:].strip() for line in lines if line.startswith("> "))
        paragraphs = re.split(r"\n\s*\n", section)
        skill_par = next((p for p in paragraphs if p.startswith("**Expected skill:**")), "")
        required, forbidden, optional = parse_expected_skills(skill_par, known)
        checks, current = [], None
        for line in lines:
            if line.startswith("- [ ] "):
                current = line[6:].strip()
                checks.append(current)
            elif current is not None and line.startswith("  ") and line.strip():
                checks[-1] = f"{checks[-1]} {line.strip()}"
            else:
                current = None
        if "**Expected result" in section:
            checks.append("The result matches the **Expected result** of the scenario.")
        cases.append({
            "id": header.group(1), "title": header.group(2).strip(), "file": path.name,
            "prompt": prompt, "required": required, "forbidden": forbidden,
            "optional": optional, "checks": checks, "section": section.strip(),
        })
    return cases


def load_cases(patterns):
    known = {p.name for p in SKILLS.iterdir() if (p / "SKILL.md").exists()}
    cases = [c for md in sorted(TESTS.glob("*.md")) if md.name != "README.md"
             for c in parse_scenarios(md, known) if c["prompt"]]
    if patterns:
        cases = [c for c in cases if any(fnmatch.fnmatch(c["id"], p) for p in patterns)]
    return cases


# --- Running Claude ---------------------------------------------------------------

def make_workspace():
    workspace = Path(tempfile.mkdtemp(prefix="geoskills-eval-"))
    shutil.copytree(TESTS / "data", workspace / "data")
    (workspace / "output").mkdir()
    target = workspace / ".claude" / "skills"
    for skill in SKILLS.iterdir():
        if (skill / "SKILL.md").exists():
            shutil.copytree(skill, target / skill.name,
                            ignore=shutil.ignore_patterns("__pycache__"))
    return workspace


def run_claude(args, prompt, cwd, tools, stream, budget):
    cmd = [args.claude, "-p", prompt, "--no-session-persistence", "--allowedTools", *tools]
    cmd += ["--output-format", "stream-json", "--verbose"] if stream else ["--output-format", "json"]
    if args.model:
        cmd += ["--model", args.model]
    if budget:
        cmd += ["--max-budget-usd", str(budget)]
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                             timeout=args.timeout).stdout
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
    events = []
    for line in out.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return events


def tool_steps(events):
    """Yield (name, input, result_text) for each tool call of a stream-json run."""
    results = {}
    for event in events:
        if event.get("type") == "user":
            for item in event.get("message", {}).get("content", []):
                if isinstance(item, dict) and item.get("type") == "tool_result":
                    content = item.get("content")
                    if isinstance(content, list):
                        content = "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
                    results[item.get("tool_use_id")] = str(content)
    for event in events:
        if event.get("type") == "assistant":
            for item in event.get("message", {}).get("content", []):
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    yield item.get("name"), item.get("input", {}), results.get(item.get("id"), "")


def loaded_skills(events):
    skills = set()
    for name, tool_input, _ in tool_steps(events):
        if name == "Skill":
            skills.add(str(tool_input.get("skill", "")).split(":")[-1])
        elif name == "Read":
            match = re.search(r"/skills/([a-z0-9-]+)/SKILL\.md$", str(tool_input.get("file_path", "")))
            if match:
                skills.add(match.group(1))
    return sorted(skills)


def transcript(events, limit=40000):
    parts = []
    for name, tool_input, result in tool_steps(events):
        parts.append(f"### Tool {name}\n{json.dumps(tool_input, ensure_ascii=False)[:1500]}\n"
                     f"--- result ---\n{result[:2500]}")
    final = next((e.get("result", "") for e in reversed(events) if e.get("type") == "result"), "")
    text = "\n\n".join(parts) + f"\n\n### Final answer\n{final}"
    return text[-limit:]


def grade(args, case, events, workspace):
    items = "\n".join(f"{i + 1}. {check}" for i, check in enumerate(case["checks"]))
    prompt = f"""You are grading an agent run for a test scenario. Do not redo the task.

Scenario (Markdown, including the prompt, the expected result and the checklist):

{case["section"]}

Items to grade:
{items}

Transcript of the agent run (tool calls, results, final answer):

{transcript(events)}

The files written by the agent are in the current directory (output/). You may inspect
them with the allowed read-only tools. Judge each item from evidence only; an item is
failed when the evidence is missing. Reply with JSON only, no prose, in this form:
{{"items": [{{"check": "<item text>", "passed": true, "evidence": "<short reason>"}}]}}"""
    result = run_claude(args, prompt, workspace, GRADER_TOOLS, stream=False,
                        budget=args.grader_budget_usd)
    text = next((e.get("result", "") for e in result if e.get("type") == "result"), "")
    try:
        return json.loads(text[text.index("{"): text.rindex("}") + 1])["items"]
    except (ValueError, KeyError):
        return [{"check": "grader output", "passed": False, "evidence": text[:500] or "no output"}]


# --- Main -------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("cases", nargs="*", help="Scenario IDs or patterns, e.g. GEO-01 'CRS-*'")
    parser.add_argument("--list", action="store_true", help="List the parsed scenarios and exit")
    parser.add_argument("--no-grade", action="store_true", help="Only check which skills load")
    parser.add_argument("--model", help="Model passed to claude --model")
    parser.add_argument("--claude", default="claude", help="Claude CLI binary")
    parser.add_argument("--timeout", type=int, default=900, help="Seconds per Claude run")
    parser.add_argument("--budget-usd", type=float, default=2.0, help="Budget per agent run")
    parser.add_argument("--grader-budget-usd", type=float, default=0.5, help="Budget per grading")
    parser.add_argument("--keep-workspaces", action="store_true", help="Keep temporary workspaces")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    if not cases:
        sys.exit("No scenario matches.")
    if args.list:
        for c in cases:
            forbidden = f" not:{','.join(c['forbidden'])}" if c["forbidden"] else ""
            print(f"{c['id']:<8} {c['file']:<28} skill={c['required'] or '-'}"
                  f"{' (optional)' if c['optional'] else ''}{forbidden} checks={len(c['checks'])}")
        return 0
    if not shutil.which(args.claude):
        sys.exit(f"Claude CLI not found: {args.claude}")

    run_dir = TESTS / "eval-results" / datetime.now().strftime("%Y%m%d-%H%M%S")
    summary = []
    for case in cases:
        print(f"{case['id']} {case['title']} ...", flush=True)
        case_dir = run_dir / case["id"]
        case_dir.mkdir(parents=True)
        workspace = make_workspace()
        start = time.time()
        events = run_claude(args, case["prompt"], workspace, AGENT_TOOLS, stream=True,
                            budget=args.budget_usd)
        loaded = loaded_skills(events)
        trigger_ok = ((case["required"] is None or case["optional"] or case["required"] in loaded)
                      and not set(case["forbidden"]) & set(loaded))
        items = [] if args.no_grade else grade(args, case, events, workspace)
        final = next((e for e in reversed(events) if e.get("type") == "result"), {})

        (case_dir / "events.ndjson").write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in events), encoding="utf-8")
        (case_dir / "answer.md").write_text(final.get("result", ""), encoding="utf-8")
        record = {
            "id": case["id"], "expected_skill": case["required"], "forbidden": case["forbidden"],
            "loaded_skills": loaded, "trigger_ok": trigger_ok,
            "passed": sum(1 for i in items if i.get("passed")), "total": len(items),
            "items": items, "seconds": round(time.time() - start),
            "cost_usd": final.get("total_cost_usd"), "workspace": str(workspace),
        }
        (case_dir / "grading.json").write_text(json.dumps(record, ensure_ascii=False, indent=2),
                                              encoding="utf-8")
        summary.append(record)
        grades = "" if args.no_grade else f", checks {record['passed']}/{record['total']}"
        print(f"  trigger {'OK' if trigger_ok else 'FAIL'} (loaded: {', '.join(loaded) or 'none'})"
              f"{grades}, {record['seconds']} s", flush=True)
        if not args.keep_workspaces:
            shutil.rmtree(workspace, ignore_errors=True)

    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    failed = [r["id"] for r in summary if not r["trigger_ok"] or r["passed"] < r["total"]]
    print(f"\n{len(summary) - len(failed)}/{len(summary)} scenarios passed. Results: {run_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
