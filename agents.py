import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent

from tools import web_search, scrape_url

load_dotenv(Path(__file__).resolve().parent / ".env")

_GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
_OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

if _GEMINI_API_KEY:
    from langchain_google_genai import ChatGoogleGenerativeAI
    active_model = "gemini-3.5-flash"
    primary_llm = ChatGoogleGenerativeAI(
        model=active_model,
        google_api_key=_GEMINI_API_KEY,
        temperature=0,
        max_output_tokens=8192,
        max_retries=3,
    )
    fallback_llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=_GEMINI_API_KEY,
        temperature=0,
        max_output_tokens=8192,
        max_retries=3,
    )
    llm = primary_llm.with_fallbacks([fallback_llm])
elif _OPENAI_API_KEY:
    from langchain_openai import ChatOpenAI
    active_model = "gpt-4o-mini"
    llm = ChatOpenAI(
        model=active_model,
        api_key=_OPENAI_API_KEY,
        temperature=0,
        max_tokens=4096,
        max_retries=2,
    )
else:
    raise ValueError("Neither GEMINI_API_KEY nor OPENAI_API_KEY was found in environment.")


# Agent 1: Web research agent
def build_search_agent():
    return create_react_agent(
        model=llm,
        tools=[web_search],
        prompt=(
            "You are a fast, high-accuracy web research agent. "
            "Execute a targeted web_search query to find recent, authoritative information. "
            "Synthesize your findings directly with source titles, URLs, and key data points. "
            "Do not make repetitive tool calls."
        ),
    )


# Agent 2: Webpage reader agent
def build_reader_agent():
    return create_react_agent(
        model=llm,
        tools=[scrape_url],
        prompt=(
            "You are an efficient web content extraction agent. "
            "Select the most authoritative URL from the search results, "
            "use scrape_url to retrieve its content, and extract key factual data, technical details, "
            "and conclusions. Preserve the source URL."
        ),
    )


# LCEL writer pipeline
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an elite research analyst and technical writer. "
        "Create comprehensive, professional, structured, and factual research reports."
    ),
    (
        "human",
        """Generate a thorough, high-quality research report based on the provided topic and gathered research.

Topic: {topic}

Research gathered:
{research}

Format your report using clean, publication-ready Markdown:

# Executive Briefing: {topic}

## 1. Executive Summary
Provide a high-impact overview of the core problem, current status, and key takeaways.

## 2. Key Findings & Technical Breakthroughs
Detail at least 3-4 specific, deep-dive findings. Use bullet points with bold subheadings and explain data points/mechanisms clearly.

## 3. Commercial & Industry Implications
Analyze market adoption, real-world deployments, competitive landscape, or practical applications.

## 4. Technical Bottlenecks & Critical Uncertainties
Discuss current limitations, engineering hurdles, regulatory concerns, or research gaps.

## 5. Strategic Outlook & Future Directions
Provide a forward-looking analysis of where this technology or topic is headed over the next 2-5 years.

## 6. Verified Sources & References
List the actual URLs and source titles retrieved during research (do not hallucinate any).

Ensure high clarity, depth, and factual grounding. Avoid fluff."""
    ),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# LCEL critic pipeline
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a rigorous research evaluator and peer reviewer. "
        "Assess accuracy, evidence grounding, completeness, depth, and clarity."
    ),
    (
        "human",
        """Critically evaluate this research report:

{report}

Provide an actionable, structured review in this exact format:

### Overall Quality Score: X/10

### Key Strengths
- **[Strength 1]**: Explanation
- **[Strength 2]**: Explanation
- **[Strength 3]**: Explanation

### Opportunities for Improvement
- **[Area 1]**: Specific actionable suggestion
- **[Area 2]**: Specific actionable suggestion

### Factual Grounding & Source Integrity
[Comment on whether citations and factual claims are supported and sound]

### Final Verdict
[One concise concluding sentence]"""
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()