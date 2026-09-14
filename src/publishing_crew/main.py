"""CLI: local checks require no model/API access; run performs a paid LLM cycle."""
import argparse
from datetime import date, datetime, timezone
from pathlib import Path
import json
import os
import uuid
from .calendar import upcoming
from .storage import database, import_catalog, save_report

def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", default="run", choices=["run", "check", "init-db", "import-catalog"])
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--days-ahead", type=int, default=90)
    parser.add_argument("--target-age", default="3-10; choose a narrower range for every concept")
    parser.add_argument("--focus", default="Positive family-focused children's stories, journals and coloring/activity books")
    parser.add_argument("--file", help="Catalog JSON file for import-catalog")
    args = parser.parse_args()
    try:
        from dotenv import load_dotenv
        load_dotenv(Path.cwd() / ".env", override=False)
    except ImportError:
        if args.command == "run":
            parser.error("Install this project first: pip install -e .")
    upcoming(args.as_of, args.days_ahead)
    if args.command == "init-db":
        with database():
            pass
        print("Catalog database initialized.")
        return
    if args.command == "import-catalog":
        if not args.file:
            parser.error("import-catalog requires --file")
        print(f"Imported {import_catalog(args.file)} catalog records.")
        return
    package = Path(__file__).resolve().parent
    guidelines = "\n\n".join(p.read_text(encoding="utf-8") for p in sorted((package / "knowledge").glob("*.md")))
    if not guidelines:
        raise RuntimeError("Missing studio guidelines")
    if args.command == "check":
        for filename in ("agents.yaml", "tasks.yaml"):
            if not (package / "config" / filename).is_file():
                raise RuntimeError(f"Missing {filename}")
        print(json.dumps(upcoming(args.as_of, args.days_ahead), indent=2))
        print("Local files and calendar checked. This does not validate provider credentials or run agents.")
        return
    if not os.getenv("MODEL", "").strip():
        parser.error("Set MODEL and the selected provider's API credentials in .env before running.")
    from .crew import PublishingCrew
    output = Path(os.getenv("PUBLISHING_OUTPUT_DIR", "output")).resolve()
    run_dir = output / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    run_dir.mkdir(parents=True)
    inputs = {"as_of": args.as_of, "days_ahead": args.days_ahead,
              "focus": args.focus, "target_age": args.target_age, "studio_guidelines": guidelines,
              "research_mode": "live web search enabled" if os.getenv("ENABLE_WEB_SEARCH", "false").lower() == "true" else "local only; demand hypotheses are unverified"}
    (run_dir / "inputs.json").write_text(json.dumps(inputs, indent=2), encoding="utf-8")
    try:
        result = PublishingCrew().crew().kickoff(inputs=inputs)
        for index, item in enumerate(result.tasks_output, start=1):
            (run_dir / f"{index:02d}-task.md").write_text(item.raw, encoding="utf-8")
            # Deterministic persistence even if an agent omits its save tool call.
            save_report(f"{run_dir.name} task {index}", item.raw)
        (run_dir / "publisher-decision.md").write_text(result.raw, encoding="utf-8")
        print(f"Completed planning cycle: {run_dir}")
    except Exception:
        (run_dir / "FAILED.txt").write_text("Run did not complete. Existing tool writes may remain. Review before retrying.\n", encoding="utf-8")
        raise

if __name__ == "__main__":
    run()
