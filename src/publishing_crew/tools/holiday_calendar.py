import json
from typing import Literal
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ..calendar import upcoming

class Input(BaseModel):
    as_of: str = Field(description="Planning date YYYY-MM-DD")
    days_ahead: int = Field(default=90, ge=1, le=730)
    publish_lead_days: int = Field(default=45, ge=0, le=365)

class HolidayCalendarTool(BaseTool):
    name: str = 'Holiday Calendar'
    description: str = 'Return US holidays and assumed production windows using an explicit as_of ISO date.'
    args_schema: type[BaseModel] = Input

    def _run(self, as_of: str, days_ahead: int = 90, publish_lead_days: int = 45) -> str:
        return json.dumps(upcoming(as_of, days_ahead, publish_lead_days), ensure_ascii=False)
