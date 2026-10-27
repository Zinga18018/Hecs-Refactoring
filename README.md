# HECS Refactoring Tool

A code-analysis and refactoring-suggestion prototype with a Flask/Socket.IO interface and a Python CLI. Python analysis uses AST heuristics for patterns such as nested loops and long functions; C++ and Rust support uses simpler text checks. Optional Ollama calls provide suggestions.

This is not a security scanner, measured optimizer, or semantics-preserving refactoring engine. The analyzer's `security_issues` and `hecs_patterns` lists are not populated by implemented detection rules.

## What the output means

- The GUI's quality, performance, and estimated-improvement scores are formulas based on issue counts, not benchmark results. Its “cyclomatic complexity” field is also an issue count.
- The CLI refactorer's AST transformation currently returns the input tree unchanged. Output is formatting or suggestion comments, not demonstrated optimization.
- The GUI's `range(len(...))` replacement is a textual demonstration that can change program behavior. Review and test any suggested code before using it.
- [Existing screenshots](Screenshots/) illustrate the interface, not correctness or measured speedups. The saved [summary](output/refactoring_summary.json) has no benchmark result.

## Development setup

```bash
git clone https://github.com/Zinga18018/Hecs-Refactoring.git
cd Hecs-Refactoring
python -m venv .venv-local
source .venv-local/bin/activate
python -m pip install -r requirements.txt
python -m pip install flask flask-socketio
```

On Windows, activate with `.venv-local\Scripts\activate`. Flask and Flask-SocketIO are imported by the GUI but omitted from [requirements.txt](requirements.txt). The repository has no Node package manifest or documented frontend build step. Dependency compatibility still needs validation.

The GUI entry point is `python gui_app.py`, serving port 5000. **Its current launcher enables debug mode on `0.0.0.0`, allows all Socket.IO origins, and uses a hard-coded development signing key. Do not expose it to a network or untrusted users.** A safe deployed service requires code/configuration changes beyond these instructions. The `/health` route also calls `jsonify` without importing it.

For the CLI, the source-defined invocation is:

```bash
python main.py ./sample_hecs_code.py --language python --output-dir ./output-local
```

Use an explicit path such as `./sample_hecs_code.py`; the analyzer's path heuristic does not recognize a bare filename. The CLI writes code and reports and attempts an AI request to its configured endpoint. GUI suggestions use Ollama's `codellama` model at localhost by default; model installation is separate. Only submit source code you are authorized to send to the chosen endpoint.

## Execution and evaluation limits

Do not use `--benchmark` on untrusted code. [benchmarker.py](src/core/benchmarker.py) launches Python files as subprocesses without a sandbox. Its memory/CPU sampling observes the parent process, and subprocess exit codes are not checked before reporting results; these are not reliable before/after resource measurements.

See [analyzer.py](src/core/analyzer.py), [refactor.py](src/core/refactor.py), [main.py](main.py), and [gui_app.py](gui_app.py) for the implemented paths. Automatic security fixes, memory-leak prevention, and performance gains are not established. No project license file is included.
