import json
from datetime import datetime

class PersistentMemory:
    def __init__(self, filename="agent_memory.json"):
        self.filename = filename
        self._ensure_file()

    def _ensure_file(self):
        try:
            with open(self.filename, "r") as f:
                pass
        except FileNotFoundError:
            with open(self.filename, "w") as f:
                json.dump({"plans": [], "tool_logs": []}, f)

    def save_plan(self, plan):
        data = self._load()
        plan["timestamp"] = datetime.now().isoformat()
        data["plans"].append(plan)
        self._save(data)

    def save_tool_log(self, log):
        data = self._load()
        data["tool_logs"].append(log)
        self._save(data)

    def get_plans(self):
        return self._load().get("plans", [])

    def get_tool_logs(self):
        return self._load().get("tool_logs", [])

    def _load(self):
        with open(self.filename, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)
