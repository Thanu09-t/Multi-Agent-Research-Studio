import json

from agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)


def _extract_content(message) -> str:
    """Normalise a LangChain message or raw string to plain text."""
    content = getattr(message, "content", message)
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


def run_research_pipeline(topic: str) -> dict:
    state = {}

    # Step 1: Web research agent
    print("\n" + "=" * 50)
    print("STEP 1 - WEB RESEARCH AGENT")
    print("=" * 50)

    search_agent = build_search_agent()

    search_result = search_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Research this topic: {topic}. "
                    "Find recent, reliable sources and provide "
                    "titles, URLs, and useful snippets."
                ),
            }
        ]
    })

    state["search_result"] = _extract_content(search_result["messages"][-1])
    print(state["search_result"])

    # Step 2: Webpage reader agent
    print("\n" + "=" * 50)
    print("STEP 2 - WEBPAGE READER AGENT")
    print("=" * 50)

    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Research topic: {topic}\n\n"
                    "Review the search results below. Select up to "
                    "three relevant HTTP/HTTPS source URLs and use "
                    "scrape_url to retrieve their content. "
                    "Summarize the evidence and preserve the URLs.\n\n"
                    f"Search results:\n{state['search_result'][:10000]}"
                ),
            }
        ]
    })

    state["scraped_content"] = _extract_content(reader_result["messages"][-1])
    print(state["scraped_content"])

    # Step 3: LCEL writer pipeline
    print("\n" + "=" * 50)
    print("STEP 3 - WRITING RESEARCH REPORT")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_result']}\n\n"
        f"SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    state["report"] = _extract_content(writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
    }))

    print(state["report"])

    # Step 4: LCEL critic pipeline
    print("\n" + "=" * 50)
    print("STEP 4 - CRITIC REVIEW")
    print("=" * 50)

    state["feedback"] = _extract_content(critic_chain.invoke({
        "report": state["report"]
    }))

    print(state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ").strip()

    if topic:
        results = run_research_pipeline(topic)

        # Save results for later use
        with open("research_report.json", "w", encoding="utf-8") as file:
            json.dump(results, file, indent=2, ensure_ascii=False)

        print("\nReport and research results saved to research_report.json")
    else:
        print("Please enter a research topic.")