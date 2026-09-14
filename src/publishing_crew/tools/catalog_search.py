import json
from typing import Literal
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ..storage import search_catalog

class Input(BaseModel):
    query: str = ""
    kind: Literal["all", "book", "character", "series"] = "all"
    limit: int = Field(default=20, ge=1, le=100)

class CatalogSearchTool(BaseTool):
    name: str = 'Search Catalog'
    description: str = 'Search local book, character and series titles/summaries. Empty query lists records; empty results mean no stored matches.'
    args_schema: type[BaseModel] = Input

    def _run(self, query: str = "", kind: str = "all", limit: int = 20) -> str:
        return json.dumps(search_catalog(query, kind, limit), ensure_ascii=False)
