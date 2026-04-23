# Tool Validator for checking tool existence and matching

class ToolValidator:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        self.tool_keywords = {
            "get_competitors": ["competitor", "identify competitors", "research competitors"],
            "fetch_ads_data": ["ad data", "collect ads", "fetch ads"],
            "analyze_trends": ["analyze trends", "trends", "trend analysis"],
            "generate_report": ["report", "generate report", "summary"],
            "fetch_marketing_news": ["news", "marketing news", "latest news", "industry news"]
        }

    def match_tool(self, task):
        task_lower = task.lower()
        for tool, keywords in self.tool_keywords.items():
            for kw in keywords:
                if kw in task_lower:
                    return tool
        return None
