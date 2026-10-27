"""Record reproducible daily repository checks without importing heavy app dependencies."""

import argparse
import ast
from datetime import date
from pathlib import Path
import subprocess
import sys


def run_check(command, root):
    result = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, type=date.fromisoformat)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    output = root / "docs" / "daily_checks" / f"{args.date.isoformat()}.md"
    if output.exists():
        print(f"Already recorded: {output.relative_to(root)}")
        return

    sources = sorted((root / "src").rglob("*.py"))
    if not sources:
        raise SystemExit("No Python source files found under src/")

    failures = []
    functions = 0
    classes = 0
    total_lines = 0
    for path in sources:
        source = path.read_text(encoding="utf-8")
        total_lines += len(source.splitlines())
        try:
            tree = ast.parse(source, filename=str(path.relative_to(root)))
        except SyntaxError as exc:
            failures.append(f"{path.relative_to(root)}: {exc.msg}, line {exc.lineno}")
            continue
        functions += sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
        classes += sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))

    compiled, compile_output = run_check([sys.executable, "-m", "compileall", "-q", "src"], root)
    test_directory = root / "tests"
    if test_directory.exists() and list(test_directory.rglob("test_*.py")):
        tests_passed, test_output = run_check(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"], root
        )
        test_status = "PASS" if tests_passed else "FAIL"
    else:
        test_status, test_output = "NOT RUN", "No unittest test_*.py files found."

    baseline = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False
    ).stdout.strip() or "unavailable"
    ast_status = "PASS" if not failures else "FAIL"
    compile_status = "PASS" if compiled else "FAIL"

    details = "\n".join(f"- {f}" for f in failures) if failures else "No syntax errors detected."
    test_output = (test_output or "(no output)")[-3000:].replace("```", "'''")
    compile_output = (compile_output or "(no output)")[-1000:].replace("```", "'''")

    report = f"""# Repository check: {args.date.isoformat()} (Asia/Kolkata)

**Automated observation, not a human coding contribution.** This report checks the repository state at the time of execution. It does not validate the app's API, market data, or financial accuracy.

- Baseline commit: `{baseline}`
- Python: `{sys.version.split()[0]}`
- Source modules: **{len(sources)}**
- Python source lines: **{total_lines}**
- Functions (including methods): **{functions}**
- Classes: **{classes}**

| Check | Result |
| --- | --- |
| Parse all `src/**/*.py` with Python AST | **{ast_status}** |
| `python -m compileall -q src` | **{compile_status}** |
| `python -m unittest discover -s tests -p 'test_*.py' -v` | **{test_status}** |

## Python parsing details

{details}

## Compile output

```text
{compile_output}
```

## Test output

```text
{test_output}
```

For actionable code improvements, review failing checks and independently verify the API and data paths.
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"Created {output.relative_to(root)}")


if __name__ == "__main__":
    main()
