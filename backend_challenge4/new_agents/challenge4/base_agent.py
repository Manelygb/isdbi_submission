import datetime
import time

class BaseAgent:
    """Base class for our mock agents."""
    agent_name = "BaseAgent"

    def __init__(self):
        # In a real Langchain agent, you'd initialize your LLM, tools, prompts here.
        # print(f"{self.agent_name} initialized.")
        pass

    def execute(self, pco: dict) -> dict:
        """
        Simulates the agent's execution.
        A real Langchain agent might have a method like `run` or `invoke`.
        """
        pco["processing_log"].append({
            "agent": self.agent_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "started"
        })
        # Simulate work
        time.sleep(0.1) # Simulate some processing time
        self._perform_task(pco)
        pco["processing_log"][-1]["status"] = "completed"
        pco["processing_log"][-1]["completed_at"] = datetime.datetime.now().isoformat()
        return pco

    def _perform_task(self, pco: dict):
        # This method will be overridden by specific agents
        raise NotImplementedError