# Children's Publishing Crew

A repository-backed CrewAI starter for a family-focused children's publishing studio.
It implements the **Market & Seasonal Researcher -> Publisher / Executive Producer**
planning workflow discussed in “Writing An Agent Prompt.”

The roles, goals and backstories in `agents.yaml` preserve the latest concise YAML
definitions from that conversation. The larger design is reflected in tasks and editable
studio guidelines. They describe a future studio; only these two agents are implemented.

## What a run produces

1. Catalog and holiday review; 5-10 ranked opportunities with evidence limitations.
2. Ideas and research saved in SQLite through the starter tools.
3. An executive concept decision, creative brief, proposed schedule and pending quality gates.
4. Markdown task results and the final brief in a unique `output/<run-id>/` folder.

This is a planning starter. It does not yet produce finished manuscripts, illustrations,
print layouts or Amazon uploads. The eventual one-book-per-day objective remains a
studio aspiration requiring the additional production roles and human reviews.

## Repository structure

```text
childrens-publishing-crew/
  pyproject.toml
  .env.example
  .gitignore
  README.md
  data/
    README.md
    manuscripts/README.md
    characters/README.md
    series/README.md
  src/publishing_crew/
    __init__.py
    crew.py
    main.py
    storage.py
    calendar.py
    config/agents.yaml
    config/tasks.yaml
    tools/
      __init__.py
      holiday_calendar.py
      catalog_search.py
      idea_bank.py
      save_research.py
      originality_check.py
    knowledge/
      brand_guidelines.md
      child_age_guidelines.md
      emotional_wellness_guidelines.md
      faith_guidelines.md
      publishing_strategy.md
      story_quality_standards.md
  tests/test_local.py
```

Runtime data lives at repository root rather than inside the installed Python package.
This keeps mutable files separate from source and makes backups easier.

## Setup

Use Python 3.11-3.13 (3.12 recommended). Extract the ZIP, then open a terminal in the
`childrens-publishing-crew` folder. The normal installation path is editable source.

Windows PowerShell:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
Copy-Item .env.example .env
.\.venv\Scripts\publishing-crew.exe check
.\.venv\Scripts\publishing-crew.exe init-db
```

macOS / Linux:
```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
cp .env.example .env
.venv/bin/publishing-crew check
.venv/bin/publishing-crew init-db
```

Edit `.env`: set `MODEL` to a CrewAI-supported model available to your account, and set
the corresponding provider credentials. `OPENAI_API_KEY` is included as an empty field
for OpenAI use. Other providers may need their own environment variable and optional
CrewAI dependency extras. No model, key or account is selected for you. Do not commit `.env`.
`check` and `init-db` make no LLM calls. `run` uses the configured model and may incur costs.

Run from the repository root so `.env` and relative data/output paths resolve consistently.
You can set absolute `PUBLISHING_DATA_DIR` and `PUBLISHING_OUTPUT_DIR` paths if needed.

## Run one planning cycle

PowerShell:
```powershell
.\.venv\Scripts\publishing-crew.exe run --days-ahead 90 --focus "Bedtime courage and family gratitude" --target-age "4-6"
```

macOS / Linux:
```bash
.venv/bin/publishing-crew run --days-ahead 90 --focus "Bedtime courage and family gratitude" --target-age "4-6"
```

`--as-of YYYY-MM-DD` overrides the default local calendar date for planning.
After activating the environment, `crewai run` is also supported through `run_crew`.
Use the `publishing-crew` command for custom arguments. No schedule is installed.

## Optional live research

Install `pip install -e ".[web]"` using your environment's Python, then set
`ENABLE_WEB_SEARCH=true` and `SERPER_API_KEY` in `.env`. The researcher receives
`SerperDevTool`. Search results provide leads, not verified sales figures or full-page analysis.
Without it, agents can still plan from the local catalog/calendar, but must label market
claims as unverified hypotheses. An LLM provider is still needed in this mode.

No Amazon sales API, Google Trends feed, unrestricted browser or website scraper is included.
Missing credentials or missing optional dependencies fail clearly when web search is enabled.

## Tools and persistent memory

| Tool | Capability | Boundary |
|---|---|---|
| Holiday Calendar | US fixed and movable holiday dates, planning offsets | Not actual demand peaks; confirm local/school dates |
| Search Catalog | Query book, character and series titles/summaries | No full manuscript or semantic search |
| Idea Bank | List/add ideas; deduplicate identical title + concept | Proposed ideas only; no publication decisions |
| Save Research | Save Markdown reports in SQLite | No arbitrary filesystem writes |
| Local Originality Check | Rank overlap with catalog/ideas | Not web plagiarism detection or rights clearance |

`data/README.md` explains catalog JSON imports. Run `publishing-crew import-catalog
--file path/to/catalog.json` to insert/update records by stable ID. Start with an empty
catalog: no fabricated books or characters are seeded. Back up the data directory.

Task outputs are also saved deterministically by the CLI, even if an agent forgets a
research save call. Agent-generated idea records still depend on successful tool calls;
review the report's returned IDs. Failed runs may leave partial tool writes and get a
`FAILED.txt` marker in their output folder. Retrying does not erase previous work.

All six knowledge files are read from the installed package and injected into task
context on each run. This starter deliberately uses direct text context rather than
embedding/RAG storage. CrewAI working memory is disabled; SQLite is the durable store.
Tool caching is disabled to prevent stale database reads and skipped writes.

## Editing and extending

Change agent identity in `agents.yaml`, assignments in `tasks.yaml`, capability wiring
in `crew.py`, and studio policies in `knowledge/`. YAML keys match decorated methods.
The two-role process is sequential. The Publisher's existing delegation setting is
preserved, but no Author, Wellness Advisor, Editor or Illustrator is created by it.

Next additions can include those specialists, structured manuscript output, catalog
librarian approval, searchable manuscript archives and production/export tools.
The current owner approval is a documented next step, not an interactive publishing gate:
there is no publishing capability attached to this crew.

## Local verification

After installation:
```bash
python -m unittest discover -s tests -v
publishing-crew check --as-of 2026-12-20 --days-ahead 150
```

Without installing CrewAI, the storage/calendar tests can run with `src` on PYTHONPATH.
Tests cover date rollover, movable holidays, persistent writes, deduplication, empty
catalog behavior, parameterized searches and atomic catalog imports. They do not
validate live model responses, commercial quality or web search results.

## GitHub

Commit this extracted project into your chosen repository. `.gitignore` excludes secrets,
local databases, manuscripts and generated output; tracked README placeholders remain.
Use the connected GitHub integration after selecting an owner/repository. This ZIP does
not create a GitHub repository or contain a remote URL or credentials.

## CrewAI references

This uses the requested Python/YAML project layout and CrewBase annotations.
- [CrewAI annotations](https://docs.crewai.com/en/learn/using-annotations)
- [Custom tools](https://docs.crewai.com/en/learn/create-custom-tools)
- [Agents](https://docs.crewai.com/en/concepts/agents)
- [Tools and optional Serper search](https://docs.crewai.com/en/concepts/tools)

Dependency ranges target CrewAI 1.x and are not a lockfile. Record resolved versions
after installation for repeatable deployments. See VALIDATION.md for checks actually run.
