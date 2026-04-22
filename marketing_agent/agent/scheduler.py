# Scheduler for converting tasks into a timeline

class Scheduler:
    def create_schedule(self, valid_tasks):
        schedule = {}
        day = 1
        for item in valid_tasks:
            task = item['task']
            if day == 1:
                phase = "Research"
            elif day == 2:
                phase = "Data Collection"
            elif day == 3:
                phase = "Analysis"
            else:
                phase = f"Execution {day}"
            schedule[f"Day {day}"] = [task]
            day += 1
        return schedule

    def create_advanced_schedule(self, valid_tasks, dependencies=None, parallel_tasks=None, deadlines=None):
        """
        Creates a schedule with dependencies, parallel tasks, and deadlines.
        dependencies: dict {task: [depends_on_task1, ...]}
        parallel_tasks: list of sets of tasks that can run in parallel
        deadlines: dict {task: deadline_date}
        """
        schedule = {}
        day = 1
        scheduled = set()
        task_map = {item['task']: item for item in valid_tasks}
        # Simple dependency resolution (topological sort)
        def can_schedule(task):
            if not dependencies or task not in dependencies:
                return True
            return all(dep in scheduled for dep in dependencies[task])
        tasks_left = [item['task'] for item in valid_tasks]
        while tasks_left:
            today_tasks = []
            for task in list(tasks_left):
                if can_schedule(task):
                    today_tasks.append(task)
            if parallel_tasks:
                # Group tasks that can run in parallel
                today_parallel = []
                for group in parallel_tasks:
                    group_ready = [t for t in group if t in today_tasks]
                    if group_ready:
                        today_parallel.extend(group_ready)
                if today_parallel:
                    today_tasks = today_parallel
            if not today_tasks:
                # Circular dependency or error
                break
            schedule[f"Day {day}"] = today_tasks
            for t in today_tasks:
                scheduled.add(t)
                if t in tasks_left:
                    tasks_left.remove(t)
            day += 1
        # Attach deadlines if provided
        if deadlines:
            for day_key, tasks in schedule.items():
                schedule[day_key] = [f"{t} (Deadline: {deadlines.get(t, 'N/A')})" for t in tasks]
        return schedule
