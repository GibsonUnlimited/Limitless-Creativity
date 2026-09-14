import json
from typing import Literal
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ..storage import list_ideas, save_idea

class Input(BaseModel):
    action: Literal["list", "add"] = "list"
    title: str = ""
    concept: str = ""
    target_age: str = ""
    product_type: str = ""
    score: float = Field(default=5, ge=1, le=10)
    limit: int = Field(default=20, ge=1, le=100)

class IdeaBankTool(BaseTool):
    name: str = "Idea Bank"
    description: str = "List saved ideas or add a proposed idea. Add requires title, concept, target_age, product_type, score 1..10. Exact repeats are deduplicated."
    args_schema: type[BaseModel] = Input

    def _run(self, action="list", title="", concept="", target_age="", product_type="", score=5, limit=20) -> str:
        if action == "list":
            result = list_ideas(limit)
        elif action == "add":
            result = save_idea(title, concept, target_age, product_type, score)
        else:
            raise ValueError("action must be list or add")
        return json.dumps(result, ensure_ascii=False)
