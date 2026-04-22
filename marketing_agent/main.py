import os
from agent.planner_agent import MarketingPlannerAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("\n=== Marketing Planning Assistant Agent ===\n")
    goal = input("Enter your high-level marketing goal: ")
    agent = MarketingPlannerAgent()
    plan = agent.run(goal)
    print("\n--- Generated Marketing Plan ---\n")
    print(plan['formatted'])

if __name__ == "__main__":
    main()
