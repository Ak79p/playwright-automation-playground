# PROJECT_CONTEXT.md

> Read this file first in every Claude Code session. Update it whenever a significant project change is made
> (new tooling, new conventions, completed/pending work, decisions, lessons learned).

Last updated: 2026-09-17 (dynamic-id tests consolidated into one module)

## 1. Purpose

AI-assisted end-to-end test automation for the public demo site **http://www.uitestingplayground.com/**.
Claude Code explores the site through the Playwright MCP server, plans scenarios, generates **Python + pytest +
Playwright** tests, and repairs them when they break. The site is a catalogue of classic UI-automation pitfalls
(dynamic ids, AJAX delays, overlapping elements, shadow DOM, hidden layers, etc.); each page is one scenario.

## 2. Architecture

```
.
├── .claude/
│   ├── PROJECT_CONTEXT.md          <- this file
│   ├── settings.json               <- approves the .mcp.json server (enabledMcpjsonServers)
│   └── agents/                     <- Playwright Test Agents (Claude Code subagents)
│       ├── playwright-test-planner.md
│       ├── playwright-test-generator.md
│       └── playwright-test-healer.md
├── .mcp.json                       <- Playwright MCP server (project scope)
├── tests/                          <- pytest suite (Python)
│   ├── conftest.py                 <- shared fixtures (viewport override)
│   ├── test_smoke.py               <- environment smoke test only
│   └── test_dynamic_id.py          <- 5 generated tests from specs/dynamic-id.md (1.1-1.5)
├── specs/                          <- markdown test plans written by the planner
│   └── dynamic-id.md               <- /dynamicid: 5 scenarios + locator guidance
├── pyproject.toml                  <- uv project; dev deps: pytest, pytest-playwright
├── pytest.ini                      <- base-url, browser, screenshots, import mode
├── uv.lock
├── .python-version                 <- 3.11
├── README.md
└── .gitignore
```

Workflow: `planner` (explore -> `specs/*.md`) -> `generator` (one scenario -> `tests/<section>/test_<scenario>.py`,
verified with `uv run pytest`) -> `healer` (run suite, reproduce failures in the MCP browser, fix, rerun).

## 3. Installed tools (verified 2026-09-17)

| Tool | Version | Notes |
|---|---|---|
| uv | 0.10.11 | project/venv manager (`uv sync`, `uv run`) |
| Python | 3.11.7 | pinned in `.python-version` |
| playwright (Python) | 1.63.0 | `uv run playwright install chromium` done |
| pytest | 9.1.1 | |
| pytest-playwright | 0.9.0 | provides `page`, `base_url`, `browser_context_args` fixtures |
| Node / npm / npx | 20.19.6 / 10.8.2 | only used to launch the MCP server via `npx` |
| @playwright/mcp | 0.0.81 (pinned) | bundles playwright-core 1.64.0-alpha; shares Chromium build 1243 |
| Claude Code | 2.1.223 | |
| Chromium | build 1243 | `~/Library/Caches/ms-playwright/chromium-1243` + headless shell |

No `package.json` / `node_modules` are kept in the repo; `npx -y` fetches the MCP package into npm's cache.

## 4. MCP configuration (`.mcp.json`, project scope)

```json
{ "mcpServers": { "playwright": { "command": "npx",
  "args": ["-y", "@playwright/mcp@0.0.81", "--headless", "--isolated",
           "--codegen", "python", "--output-dir", ".playwright-mcp"] } } }
```

- Server name `playwright` -> tools are `mcp__playwright__browser_*` (26 tools: navigate, snapshot, click, type,
  fill_form, find, hover, drag, select_option, press_key, wait_for, handle_dialog, file_upload, evaluate,
  console_messages, network_requests, take_screenshot, tabs, close, ...).
- `--codegen python`: every tool response includes the Python Playwright snippet it executed ("### Ran Playwright
  code") - the generator agent reuses those snippets.
- `--headless --isolated`: no window, fresh in-memory profile per session. Remove `--headless` to watch the agents.
- `--output-dir .playwright-mcp`: snapshots/screenshots go there; the folder is git-ignored.
- Approved project-wide via `.claude/settings.json` -> `{"enabledMcpjsonServers": ["playwright"]}`. Note:
  `claude mcp get playwright` still prints "Pending approval" (it only reads ~/.claude.json), but a fresh session
  does load all 26 tools - verified with `claude -p "list tools starting with mcp__playwright__"`.
- A session started *before* the approval will not have the tools; restart the session or run `/mcp`.

## 5. Test Agent configuration (`.claude/agents/`)

Generated from the official scaffold (`npx --package=@playwright/test playwright init-agents --loop=claude`) and
then adapted to Python. Names, roles, colors and workflows match the official agents; the differences are:

| Official (TypeScript) | This project (Python) |
|---|---|
| MCP server `playwright-test` (`npx playwright run-test-mcp-server`) | MCP server `playwright` (`@playwright/mcp`) |
| `planner_setup_page` / `planner_save_plan` | `browser_navigate` + `Write` to `specs/<name>.md` |
| `generator_setup_page` / `generator_write_test` (`.spec.ts`) | browser tools + `Write` to `tests/<section>/test_<scenario>.py`, then `uv run pytest <file>` |
| `test_run` / `test_debug` | `Bash: uv run pytest ...` + reproduce in MCP browser |
| `test.fixme()` | `@pytest.mark.skip(reason="FIXME: ...")` |
| `seed.spec.ts` | not needed; `tests/conftest.py` holds shared fixtures |

Invoke them from Claude Code with e.g. "Use the playwright-test-planner agent to plan tests for
http://www.uitestingplayground.com/ajax", then "Use playwright-test-generator for scenario 1.1 in specs/ajax.md",
then "Use playwright-test-healer to fix failing tests". All three run on `model: sonnet`.

## 6. Conventions

- Tests: Python only. **One module per test-plan section**: `tests/test_<section_slug>.py`, one function per
  scenario (`test_<scenario_slug>`), docstring = `<ordinal> <scenario title>`, `# spec:` / `# section:` header
  comments, a comment per plan step, shared constants at module level.
- Signature `def test_x(page: Page, base_url: str) -> None`; navigate via `page.goto(f"{base_url}/<path>")`.
- **Never use dynamic/generated IDs in any locator** (CSS or XPath). Prefer role/text/label/stable attributes; if
  XPath is unavoidable, key it on tag/text/class, never on the id.
- Locators: role/label/placeholder/text/test-id first; `exact=True` when names overlap; CSS/XPath only where the
  playground page deliberately demands it.
- Assertions: web-first `expect(...)`; explicit `timeout=` for slow pages; no `sleep`, `wait_for_timeout` or
  `networkidle`.
- pytest config lives in `pytest.ini` (`--base-url`, `--browser chromium`, `--screenshot only-on-failure`,
  `--output test-results`, `--import-mode=importlib`).
- Run: `uv run pytest` (all), `uv run pytest -m smoke`, `uv run pytest tests/<dir> -q`, `--headed` to watch.
- Dependencies via `uv add --dev <pkg>`; commit `uv.lock`.
- Keep this file current; the healer appends reusable findings to "Lessons learned".

## 7. Completed work

- 2026-09-17: uv project bootstrapped (Python 3.11, pytest, pytest-playwright, Chromium installed).
- 2026-09-17: Playwright MCP configured in `.mcp.json` and verified (handshake, tools/list, navigation to target).
- 2026-09-17: Planner / Generator / Healer agents created in `.claude/agents/` and verified as loaded by Claude
  Code (`claude -p` lists them) with all referenced MCP tools present on the server.
- 2026-09-17: `tests/conftest.py` + `tests/test_smoke.py`; `uv run pytest` -> 1 passed.
- 2026-09-17: README.md, .gitignore, PROJECT_CONTEXT.md written.
- 2026-09-17: MCP server approved (`.claude/settings.json`); no-dynamic-ID locator rule added to all three
  agents and to Conventions.
- 2026-09-17: First planner run (`playwright-test-planner` via `claude -p` in a fresh process) for
  http://www.uitestingplayground.com/dynamicid -> `specs/dynamic-id.md` (5 scenarios, locator guidance).
- 2026-09-17: First healer run (`playwright-test-healer`): full suite + 3 extra runs of test_dynamic_id.py,
  21/21 passed, no failures, no changes made. Workflow planner -> generator -> healer now exercised end to end.
- 2026-09-17: Consolidated `tests/dynamic_id/*.py` into `tests/test_dynamic_id.py` (user request) and fixed a
  latent flake in 1.5 (`#<id>` selector invalid when id starts with a digit -> `[id="..."]`). Suite: 6 passed.
- 2026-09-17: First generator run (`playwright-test-generator` subagent, spawned directly once the session had
  the MCP tools) -> `tests/dynamic_id/` (5 files, one per scenario). Full suite: 6 passed, no healer needed.

## 8. Pending work

- Run the planner against the remaining playground pages to produce further `specs/*.md`.
- Optionally add page objects / helper fixtures in `tests/conftest.py` once patterns emerge.
- Repo: https://github.com/Ak79p/playwright-automation-playground (branch `main`, first push 2026-09-17).

## 9. Important decisions

- **Python tests, not TypeScript.** The official Playwright agents target `@playwright/test`; we keep their
  structure but drive `uv run pytest`. The `playwright-test` MCP server was deliberately NOT configured because its
  `test_run`/`test_debug`/`generator_write_test` tools only work on a TypeScript Playwright project.
- **`@playwright/mcp` pinned to 0.0.81** for reproducible agent behaviour; bump deliberately and re-verify.
- **No committed Node project.** `npx -y` is enough to run the MCP server; avoids `package.json`/`node_modules`.
- **One module per plan section** (`tests/test_<section>.py`), user decision 2026-09-17, replacing the official
  one-file-per-scenario layout. `--import-mode=importlib` is kept in case subfolders are ever added.
- **Headless MCP browser** for unattended agent runs; switch to headed only for debugging.
- **Smoke test is not the suite.** `tests/test_smoke.py` only proves the environment works.

## 10. Lessons learned

- A test that passes once can still be flaky against random data: /dynamicid ids start with a digit about half
  the time, and `page.locator(f"#{id}")` then throws `not a valid selector`. Rerun new tests several times.
- The generator handles a whole plan section in one run (5 scenarios, ~80s, one MCP browser session); no
  need to spawn it once per scenario.
- /dynamicid emits a console error on initial load that is unrelated to the button; scenario 1.2 attaches its
  `page.on("console")` listener after `goto` and before the click so only click-caused errors are counted.
- Project `.mcp.json` servers are not loaded until approved; `enabledMcpjsonServers` in `.claude/settings.json`
  is the non-interactive way. The running session must be restarted (or `/mcp`) to pick it up - a fresh
  `claude -p ... --allowedTools "Agent,Read,Glob,Grep,Write,mcp__playwright" --permission-mode acceptEdits`
  is a workable way to run a subagent from an old session. Pipe long prompts via stdin, not `"$(cat f)"`.
- /dynamicid: button is `get_by_role("button", name="Button with Dynamic ID")`, class `btn btn-primary`; the
  id is a fresh UUID on every page load (not on click). Clicking has no visible effect - assert on URL, no
  console errors/dialogs, and the button still being visible/enabled.
- The planner may quote observed dynamic values in prose; scrub them from specs so they are never copied.
- The MCP server leaves `.playwright-mcp/` (snapshots, console logs) behind after each run; safe to delete.
- `get_by_role("link", name="Click")` on the home page is a strict-mode violation ("Click" vs "Scroll to Click");
  use `exact=True`. Expect the same for other short names on this site.
- `playwright` (Python package) has no `__version__`; use `importlib.metadata.version("playwright")`.
- `claude agents` lists running sessions, not subagent definitions; verify subagents with
  `claude -p "list custom subagents"` or by checking `.claude/agents/*.md` frontmatter.
- The MCP server writes snapshot files to its output dir relative to cwd; keep `.playwright-mcp/` git-ignored.
- A stray `VIRTUAL_ENV=/opt/anaconda3` in the shell makes `uv run` print a harmless warning; it still uses `.venv`.
