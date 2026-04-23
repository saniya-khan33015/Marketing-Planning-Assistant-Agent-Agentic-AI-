import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from agent.planner_agent import MarketingPlannerAgent
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Marketing Planning Assistant Agent", layout="wide", page_icon="🧠")

# Sidebar with project info
st.sidebar.title("🧠 Marketing Planning Assistant Agent")
st.sidebar.markdown("""
**Agentic AI Demo**

Enter a high-level marketing goal and let the agent decompose, plan, and schedule it using LLMs and multi-agent reasoning.

**Features:**
- Multi-step reasoning (Think → Act → Observe)
- Tool validation & discovery
- Task scheduling & dependencies
- CrewAI multi-agent support
- Pretty output & logs
""")
st.sidebar.info("Built with Python, Streamlit, CrewAI, and OpenRouter LLM.")

if 'agent' not in st.session_state:
    st.session_state.agent = MarketingPlannerAgent()
if 'history' not in st.session_state:
    st.session_state.history = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.title("📈 Marketing Planning Assistant Agent")

# Improved CSS for dark mode visibility
st.markdown("""
<style>
.big-font {font-size:22px !important; font-weight:600; color:#fff;}
.task-box {background:#23272f; color:#fff; padding:10px; border-radius:8px; margin-bottom:8px; border:1px solid #444;}
.insight-box {background:#1e2b1e; color:#b6fcb6; padding:10px; border-radius:8px; margin-bottom:8px; border:1px solid #2e4d2e;}
.schedule-box {background:#1e2633; color:#b3e6ff; padding:10px; border-radius:8px; margin-bottom:8px; border:1px solid #2a3b4d;}
input, textarea {color:#fff !important; background:#23272f !important;}
</style>
""", unsafe_allow_html=True)

with st.form("planner_form"):
    goal = st.text_input("🎯 Enter your high-level marketing goal:", "Analyze competitor ads")
    submitted = st.form_submit_button("🚀 Generate Plan")


if submitted or st.session_state.get('last_plan'):
    if submitted:
        with st.spinner("🤖 Agent is thinking..."):
            plan = st.session_state.agent.run(goal)
            st.session_state.history.append({"goal": goal, "plan": plan})
            st.session_state.last_plan = plan
            st.session_state.last_goal = goal
    else:
        plan = st.session_state.last_plan
        goal = st.session_state.last_goal

    # Download, Regenerate, Clear Output buttons
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.download_button(
            label="⬇️ Download Plan",
            data=plan['formatted'],
            file_name="marketing_plan.txt",
            mime="text/plain"
        )
    with col2:
        if st.button("🔄 Regenerate Plan"):
            with st.spinner("Regenerating..."):
                plan = st.session_state.agent.run(goal)
                st.session_state.last_plan = plan
                st.session_state.history.append({"goal": goal, "plan": plan})
                st.experimental_rerun()
    with col3:
        if st.button("🧹 Clear Output"):
            st.session_state.last_plan = None
            st.session_state.last_goal = None
            st.experimental_rerun()

    # Show only the most relevant similar past strategy (avoid duplicate display)
    similar_plans = st.session_state.agent.get_past_strategies(goal)
    if similar_plans:
        p = similar_plans[0]
        st.markdown(f"<div class='big-font'>🧠 <b>Similar Past Strategy</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='insight-box'><b>Goal:</b> {p['goal']}</div>", unsafe_allow_html=True)
        st.markdown("<b>Tasks:</b>", unsafe_allow_html=True)
        st.markdown("<ul>" + "".join([f"<li>{t['task']}</li>" for t in p['tasks']]) + "</ul>", unsafe_allow_html=True)
        st.markdown("<b>Insights:</b>", unsafe_allow_html=True)
        st.markdown("<ul>" + "".join([f"<li>{ins}</li>" for ins in p['insights']]) + "</ul>", unsafe_allow_html=True)

    st.markdown(f"<div class='big-font'>📝 <b>Tasks</b></div>", unsafe_allow_html=True)
    for i, item in enumerate(plan['tasks'], 1):
        st.markdown(f"<div class='task-box'> <b>{i}. {item['task']}</b> <br> <span style='color:#888'>Tool: {item['tool'] or 'N/A'}</span></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='big-font'>🤖 <b>Agent Assignment</b></div>", unsafe_allow_html=True)
    for i, item in enumerate(plan['tasks'], 1):
        st.markdown(f"<div class='task-box'> <b>{i}. {item['task']}</b> <br> <span style='color:#888'>Agent: {item.get('agent_type', 'N/A')}</span></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='big-font'>📅 <b>Schedule</b></div>", unsafe_allow_html=True)
    for day, tasks in plan['schedule'].items():
        st.markdown(f"<div class='schedule-box'><b>{day}:</b> {', '.join(tasks)}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='big-font'>💡 <b>Final Insights</b></div>", unsafe_allow_html=True)
    for insight in plan['insights']:
        st.markdown(f"<div class='insight-box'>- {insight}</div>", unsafe_allow_html=True)

    with st.expander("🧩 Agent Reasoning Steps & Log", expanded=False):
        for step in st.session_state.agent.memory:
            st.code(str(step))

    # --- Chat-style interface ---
    st.markdown("<div class='big-font'>💬 <b>Chat with the Agent</b></div>", unsafe_allow_html=True)
    chat_goal = st.text_input("Type your marketing goal or follow-up question:", "")
    if st.button("Send to Agent") and chat_goal.strip():
        with st.spinner("🤖 Agent is thinking..."):
            plan = st.session_state.agent.run(chat_goal)
            st.session_state.chat_history.append({"user": chat_goal, "agent": plan['formatted']})

    import re
    def parse_agent_response(resp):
        # Simple parser for formatted agent output
        sections = {'Tasks': [], 'Schedule': [], 'Final Insights': []}
        current = None
        for line in resp.splitlines():
            line = line.strip()
            if line.startswith('Tasks:'):
                current = 'Tasks'
                continue
            if line.startswith('Schedule:'):
                current = 'Schedule'
                continue
            if line.startswith('Final Insights:'):
                current = 'Final Insights'
                continue
            if current and (line.startswith('-') or re.match(r'\d+\.', line)):
                sections[current].append(line.lstrip('-').lstrip('0123456789. ').strip())
            elif current and line:
                sections[current].append(line)
        return sections

    for msg in reversed(st.session_state.chat_history[-10:]):
        st.markdown(f"<div class='task-box'><b>You:</b> {msg['user']}</div>", unsafe_allow_html=True)
        sections = parse_agent_response(msg['agent'])
        st.markdown(f"<div class='insight-box'><b>Agent:</b>", unsafe_allow_html=True)
        if sections['Tasks']:
            st.markdown("<b>Tasks:</b>", unsafe_allow_html=True)
            st.markdown("<ul>" + "".join([f"<li>{t}</li>" for t in sections['Tasks']]) + "</ul>", unsafe_allow_html=True)
        if sections['Schedule']:
            st.markdown("<b>Schedule:</b>", unsafe_allow_html=True)
            st.markdown("<ul>" + "".join([f"<li>{s}</li>" for s in sections['Schedule']]) + "</ul>", unsafe_allow_html=True)
        if sections['Final Insights']:
            st.markdown("<b>Final Insights:</b>", unsafe_allow_html=True)
            st.markdown("<ul>" + "".join([f"<li>{i}</li>" for i in sections['Final Insights']]) + "</ul>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# --- Analytics Dashboard ---
