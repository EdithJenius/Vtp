# Vibe-to-PRD

Drop a product idea, get a complete PRD. Hand it to Claude Code. Get your product.

**Architect** is an AI agent that turns a rough idea — even a single word — into a structured Product Requirements Document. You type the idea, Architect asks you the right questions through a structured conversation with selectable options, and it writes a full PRD as a markdown file. The agent drives. You just tap.

Built with [Agno](https://github.com/agno-agi/agno)'s UserFeedbackTools, which let agents ask structured questions with predefined options mid-conversation.

## How It Works

1. **You drop an idea** — "habit tracker", "async standup tool", anything
2. **Architect asks questions** — platform, users, features, differentiator, scope, monetization. Structured questions with selectable options, no typing required.
3. **Architect writes the PRD** — complete spec saved as markdown to `prds/`. Overview, target user, features, user journey, technical considerations, timeline, success metrics, monetization, open questions.
4. **You hand it to a coding agent** — give the markdown file to Claude Code, Codex, or whatever you use. Build the thing.

Architect learns from every session. After a few conversations, it remembers your preferences (platform, audience, product style) and adapts — skipping questions it already knows the answer to and pre-selecting smarter defaults.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/agno-agi/vibe-to-prd
cd vibe-to-prd

# Configure
cp example.env .env
# Edit .env and add your OPENAI_API_KEY

# Run
docker compose up -d --build
```

Connect to the web UI:

1. Open [os.agno.com](https://os.agno.com)
2. Add OS → Local → `http://localhost:8000`
3. Click "Connect"

## Local Development

```bash
# Set up venv and install dependencies
./scripts/venv_setup.sh && source .venv/bin/activate

# Start PostgreSQL
docker compose up -d db

# Run the CLI
python -m architect
```

## Example Vibes

```
habit tracker
Spotify but for podcast discovery
a tool that helps remote teams do async standups
Duolingo but for cooking techniques
a CLI that watches your git commits and auto-generates changelogs
```

For detailed inputs, Architect skips most questions and goes straight to the PRD:

```
I want a mobile app for freelancers to track time, generate invoices, and get paid —
Stripe integration, simple UI, no accounting degree required. Freemium model.
```

See [SAMPLE_VIBES.md](SAMPLE_VIBES.md) for more test inputs.

## Architecture

```
AgentOS (app/main.py)
└── Architect Agent (architect/agent.py)
    ├── UserFeedbackTools  → Structured questions via ask_user
    ├── FileTools          → Save PRDs to prds/
    ├── MemoryManager      → Learn user preferences across sessions
    └── PostgreSQL         → Session storage + agentic memory
```

```
vibe-to-prd/
├── app/
│   ├── main.py            # AgentOS entry point
│   └── config.yaml        # Quick prompts for web UI
├── architect/
│   ├── agent.py           # Agent definition (model, tools, memory)
│   ├── instructions.py    # Prompt (phases, PRD format, rules)
│   └── __main__.py        # python -m architect
├── db/
│   └── __init__.py        # PostgreSQL connection
├── prds/                  # Generated PRDs (gitignored)
└── scripts/
    ├── format.sh              # ruff format
    ├── validate.sh            # ruff lint + mypy
    ├── venv_setup.sh          # venv + dependency setup
    ├── generate_requirements.sh  # Regenerate requirements.txt
    ├── railway_up.sh          # First-time Railway deploy
    ├── railway_redeploy.sh    # Redeploy to Railway
    └── railway_env.sh         # Sync .env.production to Railway
```

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | — | GPT-5.4 |
| `DB_HOST` | No | `localhost` | PostgreSQL host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `DB_USER` | No | `ai` | PostgreSQL user |
| `DB_PASS` | No | `ai` | PostgreSQL password |
| `DB_DATABASE` | No | `ai` | PostgreSQL database |
| `RUNTIME_ENV` | No | `dev` | `dev` enables hot reload |
