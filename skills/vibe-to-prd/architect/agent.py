"""
Architect — turns a raw product idea into a complete PRD.

Run:
    python -m architect
"""

from pathlib import Path

from agno.agent import Agent
from agno.memory.manager import MemoryManager
from agno.models.openai import OpenAIResponses
from agno.tools.file import FileTools
from agno.tools.user_feedback import UserFeedbackTools

from architect.instructions import instructions
from db import get_postgres_db

PRDS_DIR = Path(__file__).parent.parent / "prds"

architect = Agent(
    id="architect",
    name="Architect",
    description="Drop a product idea, get a complete PRD. Asks smart questions, generates the spec.",
    model=OpenAIResponses(id="gpt-5.4"),
    db=get_postgres_db(),
    tools=[
        UserFeedbackTools(),
        FileTools(base_dir=PRDS_DIR),
    ],
    instructions=instructions,
    enable_agentic_memory=True,
    memory_manager=MemoryManager(
        db=get_postgres_db(),
        memory_capture_instructions="""\
Capture patterns from PRD sessions that would help future sessions start smarter:
- Preferred platform (e.g. "always picks mobile")
- Target audience patterns (e.g. "builds B2C consumer products")
- Product style (e.g. "prefers minimalist UX", "leans toward freemium")
- Domain interests (e.g. "interested in productivity tools", "focuses on health/fitness")
Do NOT store the PRD content itself — just the user's preferences and patterns.""",
    ),
    add_datetime_to_context=True,
    add_history_to_context=True,
    search_past_sessions=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)
