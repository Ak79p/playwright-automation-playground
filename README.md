# automation-playground

AI-assisted Playwright test automation for [UI Testing Playground](http://www.uitestingplayground.com/), using
**Python + pytest + Playwright** for the tests and **Claude Code** (Playwright MCP + Playwright Test Agents) to plan,
generate and heal them.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python 3.11 is pinned in `.python-version`)
- Node.js 18+ (only for `npx`, which launches the Playwright MCP server)
- [Claude Code](https://claude.com/claude-code)

## Setup

```bash
uv sync                              # creates .venv and installs pytest + pytest-playwright
uv run playwright install chromium   # downloads the browser
uv run pytest                        # runs the suite
```

## Running tests

```bash
uv run pytest                   # everything under tests/
uv run pytest -m smoke          # environment check only
uv run pytest --headed          # watch the browser
uv run pytest tests/<dir> -q    # one section
```

Defaults (base URL, Chromium, screenshots on failure into `test-results/`) live in `pytest.ini`.

## AI-assisted workflow (Claude Code)

Start `claude` in this directory and approve the `playwright` MCP server when prompted (defined in `.mcp.json`).
Three subagents are defined in `.claude/agents/`:

| Agent | Purpose | Output |
|---|---|---|
| `playwright-test-planner` | Explores a page with the MCP browser and writes a test plan | `specs/<name>.md` |
| `playwright-test-generator` | Executes one plan scenario live, then writes and runs a Python test | `tests/<section>/test_<scenario>.py` |
| `playwright-test-healer` | Runs `uv run pytest`, reproduces failures in the browser, fixes the test | edited tests |

Example prompts:

```
Use the playwright-test-planner agent to create a test plan for http://www.uitestingplayground.com/ajax
Use the playwright-test-generator agent to generate scenario 1.1 from specs/ajax.md
Use the playwright-test-healer agent to fix the failing tests
```

Project state, conventions and decisions are documented in `.claude/PROJECT_CONTEXT.md` — read it first in every
Claude Code session and keep it updated.

## Layout

```
tests/            pytest suite (conftest.py + generated tests)
specs/            markdown test plans written by the planner (created on first use)
.claude/agents/   planner / generator / healer subagent definitions
.claude/PROJECT_CONTEXT.md
.mcp.json         Playwright MCP server config
pytest.ini        pytest / pytest-playwright defaults
pyproject.toml    uv project + dev dependencies
```
