# 🔎 Multi-Agent Research Assistant

A simple, beginner-friendly demo of a **multi-agent research assistant** built with [LangChain](https://www.langchain.com/) and [Streamlit](https://streamlit.io/). Give it a topic and a small team of AI agents will search the web, read the sources, write a report and review it.

> This is a learning project. It is meant to be easy to read and modify, not a production system.

## How it works

The app runs four stages in sequence:

```
Topic ──► 🔍 Search agent ──► 📖 Reader agent ──► ✍️ Writer chain ──► 🧐 Critic chain ──► Report + Review
```

| Stage | Type | What it does |
|---|---|---|
| **Search agent** | LangChain agent + `web_search` tool | Searches the web with [Tavily](https://tavily.com/) and returns key findings with source URLs |
| **Reader agent** | LangChain agent + `scrape_url` tool | Scrapes the most relevant pages and summarizes what they say about the topic |
| **Writer chain** | Prompt → LLM → parser | Turns the research notes into a structured markdown report |
| **Critic chain** | Prompt → LLM → parser | Reviews the report against the notes and gives a verdict, score and suggestions |

The pipeline returns the search results, research notes, final report and critic review, so you can inspect every stage.

## Project structure

```
.
├── app.py                  # Streamlit UI
├── main.py                 # Scratch file for quick local tests
├── pyproject.toml          # Dependencies (managed with uv)
└── src/
    ├── tools/tools.py      # web_search (Tavily) and scrape_url (requests + trafilatura)
    ├── agents/agents.py    # Search agent, reader agent, writer chain, critic chain
    └── pipelines/pipeline.py  # run_pipeline(): wires the stages together
```

## Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management
- A [Tavily](https://tavily.com/) API key (used for web search)
- An API key for the LLM endpoint configured in `src/agents/agents.py`

## Getting started

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd langchain_multi_agent_simple
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up your environment variables**

   Copy the example file and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   ```env
   TAVILY_API_KEY=your-tavily-key
   OPENAI_API_KEY=your-llm-api-key
   ```
   Never commit your `.env` file. It is already listed in `.gitignore`.

4. **Run the app**
   ```bash
   uv run streamlit run app.py
   ```
   Then open the local URL Streamlit prints (usually http://localhost:8501).

A full run can take a minute or more, since the agents make several LLM and web calls in a row.

## Using the pipeline without the UI

```python
from src.pipelines.pipeline import run_pipeline

result = run_pipeline("latest developments in AI agents")

print(result["report"])   # the final markdown report
print(result["review"])   # the critic's verdict, score and suggestions
```

## Configuration

- **Model and endpoint:** edit the `ChatOpenAI(...)` setup at the top of [src/agents/agents.py](src/agents/agents.py). By default it uses an OpenAI-compatible endpoint (`base_url`) and the `openai/gpt-4.1-mini` model. Point it at any OpenAI-compatible provider you like.
- **Prompts:** the agent and chain prompts live in [src/agents/agents.py](src/agents/agents.py).
- **Scrape length:** `scrape_url` truncates page text to a fixed number of characters (`max_chars` in [src/tools/tools.py](src/tools/tools.py)). Raise it for longer pages.

## Known limitations

- `scrape_url` uses plain HTTP requests, so pages that build their content with JavaScript may return little or no text.
- The critic only reports a verdict. The pipeline does not yet loop back so the writer can revise.
- Results depend on the LLM and on what the search returns. Always check important claims against the cited sources.

## Ideas for extending it

- Add a revise loop: if the critic says `NEEDS REVISION`, send its suggestions back to the writer.
- Add a supervisor agent that decides which agent to call next.
- Summarize each scraped page before passing it on, so longer pages fit in context.
- Save reports and reviews to disk.

## Contributing

Issues and pull requests are welcome. For larger changes, please open an issue first to discuss what you'd like to change.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
