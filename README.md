# langstack-chat

A terminal chat CLI powered by LangChain + LangGraph with multi-provider support and persistent sessions.

## Features

- **Providers** — Llama.cpp (local), OpenAI, AWS Bedrock
- **Memory modes** — Stateless, In-memory, Persistent (SQLite / PostgreSQL)
- **Tools** — Web search, news, weather
- **Session management** — Resume, switch, or delete threads via `/` commands

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Quick Start

```sh
# install
git clone https://github.com/your-org/langstack-chat
cd langstack-chat
uv sync

# run
uv run langstack-chat
```

On first run it will guide you through setup.

## Usage

```
? Select provider:       Llama.cpp / OpenAI / Bedrock
? Select model:          (auto-fetched from provider)
? Select memory mode:    No memory / In-memory / Persistent
```

Type your message and press Enter. Special inputs:

| Input | Action |
|---|---|
| `/` | Open command menu (threads, model, etc.) |
| `!q` or `exit!` | Quit |

## Configuration

Config is stored at `.config/config.toml` after first run.
You can also use a `.env` file:

```env
OPENAI_API_KEY=sk-...
PSQL_URL=postgresql://username:password@localhost:5432/db
BASE_URL=http://127.0.0.1:8080/v1
```

## Logs

Logs are written to `.logs/langstack.log`. Terminal only shows warnings and errors.
