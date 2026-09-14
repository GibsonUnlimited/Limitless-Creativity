import json
from typing import Literal
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ..storage import save_report

class Input(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=100000)

class SaveResearchTool(BaseTool):
    name: str = 'Save Research'
    description: str = 'Persist a Markdown research report in SQLite. Include evidence URLs, access dates, assumptions and unknowns in content.'
    args_schema: type[BaseModel] = Input

    def _run(self, title: str, content: str) -> str:
        return json.dumps(save_report(title, content), ensure_ascii=False)
