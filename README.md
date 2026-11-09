# CSS4007 HW5 — LangGraph University IT Helpdesk

## Project Description
This project is a university IT helpdesk built with LangGraph.
It helps with Wi-Fi and password problems.
It can find instructions, check service status, and prepare ticket drafts.

## Technologies
Python 3.13.2, LangGraph 1.2.20, SQLite, OpenAI GPT-4o-mini, Pytest.

## Project Parts
- Part 1: Rule-based routing without an LLM.
- Part 2: OpenAI model with three tools.
- Part 3: Persistent conversation and user memory.
- Part 4: Automated tests and GitHub Actions.

## Installation
1. Create a virtual environment: `python -m venv .venv`
2. Activate it on Windows: `.venv\Scripts\Activate.ps1`
3. Install packages: `python -m pip install -r requirements.txt`

## API Key
Set `OPENAI_API_KEY` as an environment variable before running the model.
Never upload your API key to GitHub.

## Run
- `python part1.py`
- `python part2.py`
- `python part3.py`
- `python -m pytest tests/ -v`

Part 3 creates the memory agent; conversation demos require invoking the graph.

## Memory
Conversation history: `data/agent_memory.sqlite`
User preferences: `data/user_preferences.sqlite`
To reset memory, close the program and delete these SQLite files.

## Outputs
Execution logs and graph images are stored in `outputs/`.

## Limitations
This project uses fictional university helpdesk data.
It does not submit real support tickets.
Model demonstrations require a valid OpenAI API key.
