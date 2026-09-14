import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.holiday_calendar import HolidayCalendarTool
from .tools.catalog_search import CatalogSearchTool
from .tools.idea_bank import IdeaBankTool
from .tools.save_research import SaveResearchTool
from .tools.originality_check import OriginalityCheckTool

@CrewBase
class PublishingCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def model(self):
        model = os.getenv("MODEL", "").strip()
        if not model:
            raise ValueError("Set MODEL in .env to a model available to your provider.")
        return LLM(model=model, temperature=0.4)

    @agent
    def market_researcher(self) -> Agent:
        tools = [HolidayCalendarTool(), CatalogSearchTool(), IdeaBankTool(),
                 SaveResearchTool(), OriginalityCheckTool()]
        if os.getenv("ENABLE_WEB_SEARCH", "false").lower() == "true":
            if not os.getenv("SERPER_API_KEY", "").strip():
                raise ValueError("ENABLE_WEB_SEARCH=true requires SERPER_API_KEY.")
            try:
                from crewai_tools import SerperDevTool
            except ImportError as exc:
                raise RuntimeError("Install optional web tools: pip install -e '.[web]'") from exc
            tools.append(SerperDevTool())
        return Agent(config=self.agents_config["market_researcher"],
                     llm=self.model(), tools=tools, max_iter=35)

    @agent
    def publisher(self) -> Agent:
        return Agent(config=self.agents_config["publisher"], llm=self.model(),
                     tools=[CatalogSearchTool(), OriginalityCheckTool()], max_iter=20)

    @task
    def research_opportunities(self) -> Task:
        return Task(config=self.tasks_config["research_opportunities"])

    @task
    def publisher_review(self) -> Task:
        return Task(config=self.tasks_config["publisher_review"])

    @crew
    def crew(self) -> Crew:
        # Sequential review is sufficient for two roles. No automatic publishing.
        # Disable tool caching so repeated writes/reads reflect persistent state.
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential,
                    memory=False, cache=False, verbose=True)
