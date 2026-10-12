"""Execute documented Python recipes against independent regression fixtures."""
from pathlib import Path
import re

SKILLS = Path(__file__).resolve().parents[1] / "skills"


def run_example(reference, heading, namespace, *, example=0):
    path = SKILLS / reference
    text = path.read_text(encoding="utf-8")
    section = text.split(heading + "\n", 1)[1]
    lines = []
    in_fence = False
    for line in section.splitlines(keepends=True):
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence and re.match(r"^#{1,6} ", line):
            break
        lines.append(line)
    snippets = re.findall(r"^```python\n(.*?)^```", "".join(lines), flags=re.M | re.S)
    exec(compile(snippets[example], str(path), "exec"), namespace)
    return namespace
