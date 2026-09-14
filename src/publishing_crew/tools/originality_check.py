import json
from typing import Literal
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ..storage import originality_check

class Input(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    limit: int = Field(default=5, ge=1, le=20)

class OriginalityCheckTool(BaseTool):
    name: str = 'Local Originality Check'
    description: str = 'Compare a concept against local titles, summaries and ideas. Not web plagiarism detection or legal clearance.'
    args_schema: type[BaseModel] = Input

    def _run(self, text: str, limit: int = 5) -> str:
        return json.dumps(originality_check(text, limit), ensure_ascii=False)
