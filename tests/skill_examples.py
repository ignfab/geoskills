"""Read documented recipes and execute Python examples on regression fixtures."""
from pathlib import Path
import re

SKILLS = Path(__file__).resolve().parents[1] / "skills"


def read_example(reference, heading, *, language="python", example=0):
    path = SKILLS / reference
    text = path.read_text(encoding="utf-8")
    sections = text.split(heading + "\n")
    if len(sections) != 2:
        raise AssertionError(f"Expected one heading {heading!r} in {path}")
    section = sections[1]
    lines = []
    in_fence = False
    for line in section.splitlines(keepends=True):
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence and re.match(r"^#{1,6} ", line):
            break
        lines.append(line)
    snippets = re.findall(rf"^```{re.escape(language)}\n(.*?)^```", "".join(lines),
                          flags=re.M | re.S)
    if not 0 <= example < len(snippets):
        raise AssertionError(f"Missing {language} example {example} in {path}: {heading}")
    return snippets[example]


def run_example(reference, heading, namespace, *, example=0):
    code = read_example(reference, heading, example=example)
    exec(compile(code, str(SKILLS / reference), "exec"), namespace)
    return namespace
