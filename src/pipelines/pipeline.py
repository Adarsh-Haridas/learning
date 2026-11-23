from src.agents.agents import build_search_agent,build_reader_agent,writer_chain,critic_chain


def run_pipeline(topic: str, on_step=None) -> dict:
    """Run the research pipeline: search > read > write > critique.

    on_step: optional callback called with a progress message before each step.
    """

    def log(message: str):
        print(message)
        if on_step:
            on_step(message)

    # Step 1: Search agent finds relevant sources
    log("Step 1/4: Searching the web...")
    search_agent = build_search_agent()
    search_result = search_agent.invoke(
        {"messages": [("user", f"Find recent, reliable information about: {topic}")]}
    )
    search_output = search_result["messages"][-1].content

    # Step 2: Reader agent scrapes and summarizes the sources
    log("Step 2/4: Reading the sources...")
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Topic: {topic}\n\n"
                    f"Search findings:\n{search_output}\n\n"
                    "Pick the most relevant URLs from the findings above, "
                    "scrape them, and summarize what they say about the topic.",
                )
            ]
        }
    )
    research = reader_result["messages"][-1].content

    # Step 3: Writer chain turns the research into a report
    log("Step 3/4: Writing the report...")
    report = writer_chain.invoke({"topic": topic, "research": research})

    # Step 4: Critic chain reviews the report
    log("Step 4/4: Reviewing the report...")
    review = critic_chain.invoke(
        {"topic": topic, "research": research, "report": report}
    )

    return {
        "topic": topic,
        "search_results": search_output,
        "research": research,
        "report": report,
        "review": review,
    }