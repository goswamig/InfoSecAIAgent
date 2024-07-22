import coordinator
class ReportingAgent:
    def run(self, results):
        report = "Cybersecurity Assessment Report\n"
        report += "==============================\n\n"
        for result in results:
            report += result + "\n\n"
        return report

coordinator.add_agent(ReportingAgent())


target = "example.com"
results = coordinator.run_security_assessment(target)
final_report = coordinator.agents[-1].run(results)  # The last agent is the ReportingAgent

print(final_report)