# HW5 — My LangGraph helpdesk

## Part 1 — How the graph works

### My graph and state

I created a LangGraph helpdesk without an LLM.

Original graph:

START → read_request
- wifi → wifi_help → END
- password → password_help → END
- other → other_help → END

The graph uses three state fields:
- message: the original user message.
- category: the detected problem type.
- reply: the final helpdesk response.

The read_request node reads the message and updates category.
The wifi_help node reads instructions from helpdesk.json and updates reply.
The password_help node reads password instructions and updates reply.
The other_help node returns a clarification question.

A node returns changes to the state. A conditional edge chooses which node runs next.

The next node receives the current graph state, including previous updates.

START is the beginning of the graph. END finishes execution.
Compiling the graph prepares it for execution.

### Predictions before running

| Message | Predicted route | Actual route | What I learned |
| --- | --- | --- | --- |
| I cannot connect to Wi-Fi. | read_request → wifi_help | read_request → wifi_help | Wi-Fi is detected correctly. |
| I forgot my PASSWORD. | read_request → password_help | read_request → password_help | Routing ignores letter case. |
| My laptop screen is broken. | read_request → other_help | read_request → other_help | Unknown topics require clarification. |
| My Wi-Fi password does not work. | read_request → wifi_help | read_request → wifi_help | Wi-Fi has priority in the original rules. |

The original execution traces are saved in outputs/part1_original_trace.json.

### My change to the graph

I added a new node called clarify_problem.

Updated graph:

START → read_request
- wifi → wifi_help → END
- password → password_help → END
- other → other_help → END
- clarify → clarify_problem → END

When a message contains both Wi-Fi and password, the graph now asks which problem should be solved first.

Example message:
My Wi-Fi password does not work.

New execution route:
START → read_request → clarify_problem → END

Final category: clarify

Final reply:
You mentioned Wi-Fi and password. Which problem should we solve first?

The updated trace is saved in outputs/part1_updated_trace.json.
The updated graph image is saved in outputs/part1_graph.png.

LangGraph controls the execution order, state updates and transitions.
My Python functions decide the category and generate the helpdesk response.
No language model is used in Part 1.

## Part 2 — Model and tools

### Model and provider

I used OpenAI GPT-4o-mini with LangGraph.

The model chooses which tool to call.
LangGraph controls the execution flow.

### Tools

I created three tools:

1. find_instructions — reads Wi-Fi and password instructions.
2. check_service_status — checks if a service is working.
3. prepare_ticket — creates a local support ticket draft.

All three tools can work independently.

### Model and tool loop

START → model → tools → model → END

If the model requests a tool, LangGraph sends the request
to the tools node.

The tools node executes the tool and returns the result.

The result is added to the message history.
The model then decides whether to use another tool or answer.

### Answers to the four questions

1. The graph checks whether the last AI message has tool calls.
   If yes, it runs tools. Otherwise, it ends.

2. The OpenAI model requests a tool.
   The LangGraph tools node executes it.

3. After a tool runs, its result is added to the messages state.

4. Part 1 uses fixed Python routing rules.
   Part 2 uses a language model to choose tools.

### Loop limit

I added MAX_STEPS = 5.

This prevents the agent from continuing the tool loop forever.

### Demonstrations

I tested Wi-Fi instructions, password instructions,
service outages, unknown service status, and missing ticket details.

Saved examples include:

- outputs/part2_multiple_tools.json
- outputs/part2_loop_limit.json
- outputs/S07_wifi_outage.json
- outputs/S08_status_unknown.json
- outputs/S09_missing_details.json
- outputs/S14_password_outage.json

The ticket tool creates a draft only.
It does not send a real support ticket.

## Part 3 — Memory

### Conversation memory

I used SQLite and LangGraph SqliteSaver.
The agent saves previous messages in a conversation.
A thread_id identifies one conversation.
The same thread_id allows the agent to restore its history.

### User memory

I used SqliteStore to save user preferences.
A user_id identifies a user, not a conversation.
One user can have different conversation threads.

The preferences are saved under a user-specific namespace.
This keeps different users' preferences separate.

### Memory examples

User student_001 prefers simple English at A2 level.
User student_002 prefers Russian at B1 level.

I tested that preferences can be saved and restored.
I also tested that different users have different preferences.

### Conversation persistence

The checkpointer saves conversation state in SQLite.
I tested restoring a saved message after creating a new graph.
This test does not require an OpenAI API key.

### Retrieval and memory

Reading Wi-Fi instructions from helpdesk.json is retrieval.
Remembering a user's language preference is user memory.
Remembering previous messages is conversation memory.

### Storage

Conversation database: data/agent_memory.sqlite
User preferences database: data/user_preferences.sqlite

The SQLite databases are not uploaded to GitHub.
They can be recreated when the program starts.

## Part 4 — Running and checking my work

### Environment

I used Python 3.13.2.
All package versions are saved in requirements.txt.
README.md explains how to install and run the project.

### Automated tests

I created automated tests using pytest.

Part 2 has six tests:
- Wi-Fi instructions
- Password instructions
- Wi-Fi service status
- Password service outage
- Missing ticket details
- Unknown service

These tests catch problems in tool outputs and status handling.

Part 3 has three tests:
- Saved user preferences after reconnecting
- Separation of preferences between users
- Conversation history after reconnecting

These tests catch memory persistence and user isolation errors.

### Test results

Command: python -m pytest tests/ -v

Local result: 9 passed, 0 failed.

The tests do not call the OpenAI API.
They test tools and SQLite memory directly.
No fake model is used in these tests.

### GitHub Actions

Workflow file: .github/workflows/tests.yml

The workflow installs Python 3.13 and project dependencies.
It runs pytest after each push and pull request.
The workflow also supports manual execution.

GitHub Actions results will be checked after pushing.

### Security

The .gitignore file excludes API keys and SQLite databases.
The project uses fictional user identifiers.
No real support tickets are submitted.

## Choices and limitations

### My choices

I chose LangGraph because it controls the agent's steps.
It supports conditional routing, tools, and memory.

I used OpenAI GPT-4o-mini to choose tools in Part 2.
The model can select tools based on the user's request.

I used SQLite because it is simple and saves data locally.
SqliteSaver stores conversation history.
SqliteStore stores user language preferences.

I used pytest to check the tools and memory.
The automated tests do not need an OpenAI API key.

### Limitations

The agent uses fictional university helpdesk data.
It only supports a small number of problem categories.
The service status is simulated, not live.
Support tickets are drafts and are not submitted.

The model requires internet access and an API key.
Model answers can vary between runs.

The SQLite databases are local to one computer.
The project is a learning prototype, not a production system.

## Supplied scenarios — my actual results

| Scenario | Command or manual steps | Log file | What happened / what I changed |
| --- | --- | --- | --- |
| S01 — Simple Wi-Fi route | Saved execution | outputs/part1_original_trace.json | Wi-Fi request routed to wifi_help. |
| S02 — Case-insensitive password route | Saved execution | outputs/part1_original_trace.json | Uppercase PASSWORD routed to password_help. |
| S03 — Unsupported request | Saved execution | outputs/part1_original_trace.json | Unsupported request routed to other_help. |
| S04 — Two topics before the graph change | Saved execution | outputs/part1_original_trace.json | Original graph gave Wi-Fi priority. |
| S05 — Two topics after adding clarification | Saved execution | outputs/part1_updated_trace.json | Both topics routed to clarify_problem. |
| S06 — Instructions then local ticket | Run Part 2 agent | outputs/part2_multiple_tools.json | Agent used three tools and prepared a ticket draft. |
| S07 — The same request during a Wi-Fi outage | Saved execution | outputs/S07_wifi_outage.json | Agent detected that Wi-Fi was down. |
| S08 — Status source unavailable | Saved execution | outputs/S08_status_unknown.json | Agent explained that status was unknown. |
| S09 — Missing ticket details | Saved execution | outputs/S09_missing_details.json | Tool requested missing ticket details. |
| S10 — Use the current conversation | Saved execution | outputs/S10_conversation_memory.json | Agent recalled the previous Wi-Fi problem. |
| S11 — Persist and recall after restart | Saved execution | outputs/S11_memory_persistence.json | Conversation restored in a new agent instance. |
| S12 — Preference across threads without replay | Saved execution | outputs/S12_preference_across_threads.json | Agent used saved A2 English preference in a new thread. |
| S13 — Do not share memory between users | Saved execution | outputs/S13_user_memory_isolation.json | Users had separate preferences; student_002 received a Russian answer. |
| S14 — Password recovery outage | Saved execution | outputs/S14_password_outage.json | Agent detected password recovery outage. |
