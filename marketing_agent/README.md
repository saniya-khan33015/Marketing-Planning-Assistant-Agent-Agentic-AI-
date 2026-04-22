# Group Number: 08 D12
# Marketing Planning Assistant Agent

An intelligent agent that takes a high-level marketing goal and autonomously breaks it into structured tasks, reasons through execution, validates tool availability, manages dependencies, schedules tasks, and generates a final marketing plan.

## Features
- LLM-powered Planner Agent (CrewAI/LangChain)
- Multi-step reasoning loop (Think → Act → Observe)
- Tool validation and dependency management
- Mock tools for demonstration
- Task scheduler
- Structured output (tasks, schedule, insights)
- Optional Streamlit UI
- Logging and memory of agent steps

## Project Structure
```
marketing_agent/
│
├── main.py
├── agent/
│   ├── planner_agent.py
│   ├── tools.py
│   ├── scheduler.py
│   ├── validator.py
│
├── utils/
│   └── llm_handler.py
│
├── ui/
│   └── app.py
│
├── requirements.txt
├── .env
└── README.md
```

## Setup Instructions

1. **Clone the repository** (if not already):
   ```sh
   git clone <repo-url>
   cd marketing_agent
   ```

2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure API keys**:
   - Copy `.env` and fill in your `OPENAI_API_KEY` or `OPENROUTER_API_KEY`.
   - Set `LLM_PROVIDER` to `openai` or `openrouter`.

4. **Run the CLI app**:
   ```sh
   python main.py
   ```

5. **(Optional) Run the Streamlit UI**:
   ```sh
   streamlit run ui/app.py
   ```

## Example Usage

**Input:**
```
Analyze competitor ads
```

**Output:**
```
Tasks:
  1. Identify competitors
  2. Collect ad data
  3. Analyze creatives
  4. Compare strategies

Schedule:
  Day 1: Competitor Research
  Day 2: Data Collection
  Day 3: Analysis

Final Insights:
  - Identify competitors: ['BrandA', 'BrandB', 'BrandC']
  - Collect ad data: [{'brand': 'BrandA', 'ads': 12}, {'brand': 'BrandB', 'ads': 8}]
  - Analyze creatives: {'trend': 'Video ads increasing', 'platform': 'Instagram'}
  - Compare strategies: Report generated: Competitor ad strategies summarized.
```

## Notes
- The agent uses mock tools for demonstration. Integrate real APIs for production.
- All code is modular and production-ready with comments for clarity.

## Group Members
Saniya Khan :- EN22IT301091
Gaurav Raudhale :- EN22IT301036
Vedant Meena :- EN22IT301120
Soham Khushwah :- EN22IT301104
