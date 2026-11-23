from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search,scrape_url


load_dotenv()

#Model Initialization
llm = ChatOpenAI(
    base_url="https://api.meshapi.ai/v1",
    model="openai/gpt-4.1-mini",
    temperature=0.0
)

# 1st Agent: Search Agent
def build_search_agent():
    """Create the search agent, which uses web_search to find relevant sources."""
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are a search agent in a research team. "
            "Use the web_search tool to find relevant, up-to-date information "
            "for the user's topic. Run more than one search with different "
            "queries if needed. Return the key findings along with the source "
            "URLs for each one. Do not make up information or URLs."
        ),
    )


# 2nd Agent: Reader Agent
def build_reader_agent():
    """Create the reader agent, which uses scrape_url to read pages in depth."""
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are a reader agent in a research team. "
            "You are given one or more URLs. Use the scrape_url tool to read "
            "each page, then extract the facts, data and arguments relevant to "
            "the research topic. Summarize each page concisely and keep the "
            "source URL with each summary. If a page cannot be scraped, say so "
            "and move on. Do not make up content that is not on the page."
        ),
    )

# writer chain

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are the writer in a research team. You turn research notes into a "
        "clear, well-structured report. Use only the information in the "
        "research notes. Do not add facts that are not in them. If the notes "
        "are thin or conflicting, say so.\n\n"
        "Format the report in markdown with these sections:\n"
        "# <Title>\n"
        "## Summary: 2-3 sentences with the main takeaway\n"
        "## Key Findings: a bulleted list of the most important points\n"
        "## Details: short paragraphs covering the topic in more depth\n"
        "## Sources: a list of the source URLs used\n\n"
        "Keep the tone neutral and easy to read.",
    ),
    (
        "human",
        "Topic: {topic}\n\n"
        "Research notes:\n{research}\n\n"
        "Write the report.",
    ),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# critic chain

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are the critic in a research team. You review a report written "
        "from research notes and judge its quality. Be fair but strict.\n\n"
        "Check the report for:\n"
        "- Accuracy: every claim is supported by the research notes\n"
        "- Completeness: the main points of the topic are covered\n"
        "- Clarity: the structure and writing are easy to follow\n"
        "- Sources: URLs are listed and come from the research notes\n\n"
        "Respond in this format:\n"
        "## Verdict: APPROVED or NEEDS REVISION\n"
        "## Score: a number from 1 to 10\n"
        "## Strengths: a bulleted list\n"
        "## Issues: a bulleted list of specific problems, or 'None'\n"
        "## Suggestions: concrete changes the writer should make, or 'None'",
    ),
    (
        "human",
        "Topic: {topic}\n\n"
        "Research notes:\n{research}\n\n"
        "Report to review:\n{report}\n\n"
        "Write your review.",
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()