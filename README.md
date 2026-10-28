# Multi-Agent Research Studio

An autonomous, multi-agent AI research studio built with **Python**, **LangChain**, **LangGraph**, and **Streamlit**. 

The Studio orchestrates a specialized 4-stage sequential agent pipeline that searches the live web, extracts deep webpage content, synthesizes structured technical reports, and performs automated adversarial peer reviews.

---

## Architecture Overview

```text
multi-agent-research-studio/
├── agents.py            # LangChain & LangGraph agents (Search, Reader, Writer, Critic)
├── app.py               # Professional Streamlit UI with live stage stepper & metrics
├── pipeline.py          # Deterministic 4-stage research pipeline with event callbacks
├── tools.py             # Tavily search & high-speed web content extraction tools
├── requirements.txt     # Python production dependencies
├── requirement.txt      # Dependency specification
├── Dockerfile           # Production Docker container setup
├── .dockerignore        # Container build ignore rules
├── .gitignore           # Git ignore patterns (protects secrets and venv)
├── .env.example         # Template for environment configuration
└── README.md            # Documentation
```

---

## Multi-Agent Pipeline

1. **Discovery Agent (`Search Agent`)**:
   - Queries the live web using the **Tavily Search API**.
   - Identifies high-relevance URLs, authoritative technical sources, and summaries.

2. **Content Extraction Agent (`Reader Agent`)**:
   - Uses Tavily's native high-speed `extract()` endpoint (backed by an expedited HTTP fallback).
   - Bypasses anti-bot walls and cleans DOM trees to extract clean technical context.

3. **Synthesis Writer (`LangChain Chain`)**:
   - Synthesizes findings using **Google Gemini 3.5 Flash** (with resilient fallback to `gemini-3.5-flash-lite`, or OpenAI models).
   - Generates an in-depth markdown report structured with Executive Summaries, Key Findings, Strategic Implications, Bottlenecks, and References.

4. **Quality Critic Agent (`LangChain Chain`)**:
   - Conducts rigorous peer review against empirical depth and source integrity criteria.
   - Outputs a 10-point evaluation score, strengths, and areas for improvement.

---

## Quickstart

### 1. Clone & Configure Environment

```bash
git clone https://github.com/Thanu09-t/Multi-Agent-Research-Studio.git
cd Multi-Agent-Research-Studio

# Copy environment template
cp .env.example .env
```

Edit `.env` with your API credentials:
```env
TAVILY_API_KEY=tvly-...
GEMINI_API_KEY=AIzaSy...
```

### 2. Install Dependencies

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Studio

```bash
streamlit run app.py
```

Access the UI at `http://localhost:8501`.

---

## Docker Deployment

```bash
# Build the image
docker build -t research-studio .

# Run with environment variables
docker run -d -p 8501:8501 --env-file .env research-studio
```

---

## Streamlit Community Cloud Deployment

1. Fork or push this repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Click **New app** and select:
   - **Repository:** `Multi-Agent-Research-Studio`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Expand **Advanced settings → Secrets** and add your credentials in TOML format:
   ```toml
   TAVILY_API_KEY = "tvly-..."
   GEMINI_API_KEY = "..."
   ```
5. Click **Deploy**. The application will automatically build and launch.
