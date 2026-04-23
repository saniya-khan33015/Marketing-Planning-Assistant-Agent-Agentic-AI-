# CrewAI and core modules
from agent.tools import TOOL_REGISTRY
from agent.validator import ToolValidator
from agent.scheduler import Scheduler
from utils.llm_handler import LLMHandler
from utils.persistent_memory import PersistentMemory
from datetime import datetime
import traceback
try:
    from crewai import Agent, Task, Crew, Process
except ImportError:
    Agent = Task = Crew = Process = None  # Fallback if CrewAI not installed
from agent.tools import tool_execution_log


class MarketingPlannerAgent:
    """
    Main orchestrator for the Marketing Planning Assistant Agent.
    Uses CrewAI for multi-step reasoning and agent workflow if available.
    Logs all steps and produces pretty, robust output.
    """
    def __init__(self):
        self.llm = LLMHandler()
        self.validator = ToolValidator(TOOL_REGISTRY)
        self.scheduler = Scheduler()
        self.memory = []  # For logging steps
        self.memory_store = PersistentMemory()
        self.log("Agent initialized.")

    def run(self, goal):
        """
        Main entry point. Runs the agentic workflow for a given marketing goal.
        """
        self.memory = []
        self.log(f"Received goal: {goal}")
        try:
            # Step 1: Decompose goal into tasks
            tasks = self.decompose_goal(goal)
            # Step 2: Validate tools and resolve dependencies
            valid_tasks = self.validate_and_order_tasks(tasks)
            # Step 2.5: Assign specialized agents to tasks
            valid_tasks = self.assign_agents_to_tasks(valid_tasks)
            # Step 3: Schedule tasks
            schedule = self.scheduler.create_schedule(valid_tasks)
            # Step 4: Execute tasks with reasoning loop (always use custom logic for OpenRouter)
            results, insights = self.execute_tasks(valid_tasks)
            # Step 5: Format output
            formatted = self.format_output(valid_tasks, schedule, insights)
            # Step 6: Save plan to persistent memory
            self.memory_store.save_plan({
                'goal': goal,
                'tasks': valid_tasks,
                'schedule': schedule,
                'insights': insights
            })
            return {
                'tasks': valid_tasks,
                'schedule': schedule,
                'insights': insights,
                'formatted': formatted
            }
        except Exception as e:
            tb = traceback.format_exc()
            self.log(f"ERROR: {e}\n{tb}")
            return {
                'tasks': [],
                'schedule': {},
                'insights': [f"Error: {e}"],
                'formatted': f"An error occurred: {e}\n{tb}"
            }

    def decompose_goal(self, goal):
        """
        Uses LLM to break down the goal into actionable tasks.
        """
        prompt = (
            "Break down the following marketing goal into a numbered list of actionable, atomic tasks. "
            "Be concise and logical.\nGoal: " + goal
        )
        response = self.llm.complete(prompt)
        tasks = self.parse_tasks(response)
        self.log(f"Decomposed goal into tasks: {tasks}")
        return tasks

    def parse_tasks(self, response):
        """
        Parses LLM response into a list of tasks.
        """
        tasks = []
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line[0].isdigit() or line.startswith('-'):
                task = line.split('.', 1)[-1].strip() if '.' in line else line.strip('- ').strip()
                if task:
                    tasks.append(task)
        return tasks

    def validate_and_order_tasks(self, tasks):
        """
        Validates tool availability for each task and orders them.
        """
        valid_tasks = []
        for task in tasks:
            tool = self.validator.match_tool(task)
            valid_tasks.append({'task': task, 'tool': tool})
        self.log(f"Validated and ordered tasks: {valid_tasks}")
        return valid_tasks

    def assign_agents_to_tasks(self, valid_tasks):
        """
        Assigns specialized agents to each task.
        """
        for item in valid_tasks:
            item['agent_type'] = self.assign_agent(item['task'])
        return valid_tasks

    def execute_tasks(self, valid_tasks):
        """
        Default multi-step reasoning loop (Think → Act → Observe) if CrewAI is not available.
        """
        results = {}
        insights = []
        for idx, item in enumerate(valid_tasks):
            task = item['task']
            tool = item['tool']
            agent_type = item.get('agent_type', 'N/A')
            self.log(f"[THINK] Step {idx+1}: {task} | Tool: {tool if tool else 'N/A'} | Agent: {agent_type}")
            if tool:
                result, status, error = self.execute_task_with_tracking(tool)
                results[task] = result
                if status == "success":
                    insights.append(f"{task}: {result}")
                    self.log(f"[ACT] Called tool '{tool}' for '{task}'. [OBSERVE] Result: {result}")
                elif status == "not_found":
                    insights.append(f"{task}: Tool not found.")
                    self.log(f"[ERROR] Tool '{tool}' not found for '{task}'.")
                else:
                    insights.append(f"{task}: Tool error: {error}")
                    self.log(f"[ERROR] Tool '{tool}' failed: {error}")
            else:
                results[task] = None
                insights.append(f"{task}: Tool not available.")
                self.log(f"[SKIP] No tool for '{task}'.")
        return results, insights

    def crewai_execute_tasks(self, valid_tasks):
        """
        Uses CrewAI for multi-agent, multi-step execution if available.
        """
        # Define agents for each tool type (mocked for demo)
        agents = {}
        for item in valid_tasks:
            tool = item['tool']
            if tool and tool not in agents:
                agents[tool] = Agent(
                    name=tool,
                    role=f"Executes {tool}",
                    goal=f"Run {tool} for marketing planning.",
                    backstory=f"A specialist in {tool} for marketing workflows."
                )
        # Create CrewAI tasks
        crew_tasks = []
        for idx, item in enumerate(valid_tasks):
            tool = item['tool']
            task_desc = item['task']
            if tool and tool in agents:
                crew_tasks.append(Task(
                    description=task_desc,
                    expected_output="Return result of the tool call.",
                    agent=agents[tool],
                    callback=TOOL_REGISTRY[tool]
                ))
            else:
                # Assign a default 'General' agent if no tool is available
                if "General" not in agents:
                    agents["General"] = Agent(
                        name="General",
                        role="Handles general marketing tasks",
                        goal="Provide general support for marketing planning.",
                        backstory="A reliable assistant for any marketing-related task, always ready to help when no specialist is available."
                    )
                crew_tasks.append(Task(
                    description=task_desc,
                    expected_output="No tool available.",
                    agent=agents["General"],
                    callback=lambda: None
                ))
        # Run CrewAI process
        crew = Crew(
            agents=list(agents.values()),
            tasks=crew_tasks,
            process=Process.sequential
        )
        results = crew.kickoff()
        # Map results to insights
        insights = []
        for idx, item in enumerate(valid_tasks):
            task = item['task']
            result = results[idx] if idx < len(results) else None
            insights.append(f"{task}: {result}")
            self.log(f"[CREWAI] {task}: {result}")
        return results, insights

    def format_output(self, valid_tasks, schedule, insights):
        """
        Pretty-formats the final output for CLI and UI.
        """
        out = []
        out.append("\n\033[1mTasks:\033[0m")
        for i, item in enumerate(valid_tasks, 1):
            out.append(f"  {i}. {item['task']}")
        out.append("\n\033[1mSchedule:\033[0m")
        for day, tasks in schedule.items():
            out.append(f"  {day}: {', '.join(tasks)}")
        out.append("\n\033[1mFinal Insights:\033[0m")
        for insight in insights:
            out.append(f"  - {insight}")
        out.append("\n\033[1mAgent Log:\033[0m")
        for log in self.memory:
            out.append(f"    {log}")
        # Show agent assignment in output
        out.append("\n\033[1mAgent Assignment:\033[0m")
        for i, item in enumerate(valid_tasks, 1):
            out.append(f"  {i}. {item['task']} → {item.get('agent_type', 'N/A')}")
        return '\n'.join(out)

    def log(self, message):
        """
        Logs a message with timestamp to agent memory.
        """
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.memory.append(f"[{ts}] {message}")

    def get_specialized_agents(self):
        """
        Returns a dictionary of specialized agents for multi-agent workflow.
        """
        return {
            'Research': {
                'name': 'Research Agent',
                'role': 'Performs market and competitor research',
                'goal': 'Gather and analyze marketing data',
            },
            'Strategy': {
                'name': 'Strategy Agent',
                'role': 'Develops marketing strategies',
                'goal': 'Formulate actionable marketing strategies',
            },
            'Content': {
                'name': 'Content Agent',
                'role': 'Creates marketing content',
                'goal': 'Generate engaging marketing content',
            },
            'Analytics': {
                'name': 'Analytics Agent',
                'role': 'Analyzes campaign performance',
                'goal': 'Evaluate and report on marketing outcomes',
            },
        }

    def assign_agent(self, task):
        """
        Assigns a specialized agent type to a task based on keywords.
        """
        task_lower = task.lower()
        if any(word in task_lower for word in ['research', 'analyze', 'find', 'collect', 'discover']):
            return 'Research'
        if any(word in task_lower for word in ['strategy', 'plan', 'approach', 'framework']):
            return 'Strategy'
        if any(word in task_lower for word in ['content', 'write', 'create', 'generate', 'copy', 'ad']):
            return 'Content'
        if any(word in task_lower for word in ['analyz', 'metric', 'report', 'measure', 'evaluate']):
            return 'Analytics'
        return 'Research'  # Default fallback

    def execute_task_with_tracking(self, tool, task_input=None):
        """
        Executes a tool, tracks input/output/success/failure, and logs the result.
        """
        from agent.tools import tool_execution_log
        result = None
        status = "success"
        error = None
        try:
            if tool in TOOL_REGISTRY:
                if task_input is not None:
                    result = TOOL_REGISTRY[tool](task_input)
                else:
                    result = TOOL_REGISTRY[tool]()
            else:
                result = None
                status = "not_found"
        except Exception as e:
            result = None
            status = "error"
            error = str(e)
        log_entry = {
            'tool': tool,
            'input': task_input,
            'output': result,
            'status': status,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        tool_execution_log.append(log_entry)
        self.memory_store.save_tool_log(log_entry)
        return result, status, error

    def retrieve_similar_past_plans(self, goal, top_k=3):
        """
        Retrieves the most similar past plans to the current goal.
        """
        from difflib import SequenceMatcher
        plans = self.memory_store.get_plans()
        scored = []
        for plan in plans:
            past_goal = plan.get('goal', '')
            score = SequenceMatcher(None, goal.lower(), past_goal.lower()).ratio()
            scored.append((score, plan))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [plan for score, plan in scored[:top_k] if score > 0.3]  # Only return if reasonably similar

    def get_past_strategies(self, goal):
        """
        Public method to get similar past strategies for a goal.
        """
        return self.retrieve_similar_past_plans(goal)
