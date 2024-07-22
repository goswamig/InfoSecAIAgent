class CoordinatorAgent:
    def __init__(self):
        self.agents = []

    def add_agent(self, agent):
        self.agents.append(agent)

    def run_security_assessment(self, target):
        results = []
        for agent in self.agents:
            results.append(agent.run(target))
        return results

coordinator = CoordinatorAgent()
