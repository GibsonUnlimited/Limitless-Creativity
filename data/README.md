# Persistent publishing data
Run `publishing-crew init-db` to create `publishing.db` here. It is intentionally absent
from the ZIP and Git. `PUBLISHING_DATA_DIR` can point to another durable directory.

Tables: `catalog` (books, characters, series), `ideas`, `research_reports`.
Catalog fields: id, kind, title, summary, metadata_json. Ideas include proposed status,
target age, format and score. Research stores full Markdown including source citations.
Only ideas/research can be written by the researcher tools. Catalog import is an owner CLI action.

Import your own records with `publishing-crew import-catalog --file path/to/catalog.json`.
The JSON is a list; each entry needs id, kind (`book`, `character`, `series`), title, summary,
and optional metadata object. IDs are stable: importing an existing ID updates that record.

Example (illustrative only; not a real catalog entry):
```json
[{"id":"BK-001","kind":"book","title":"Your book title","summary":"Your plot summary",
  "metadata":{"target_age":"4-6","status":"draft","manuscript_path":"manuscripts/BK-001.md"}}]
```

The three folders hold files you add. They are not automatically indexed or populated.
Search currently covers catalog titles/summaries; add approved manuscript retrieval or a
vector index later. Back up this directory and any custom data directory while the app is stopped.
Do not treat CrewAI working memory as the authoritative catalog. Runtime content is ignored by Git.
