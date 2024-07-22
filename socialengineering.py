class SocialEngineeringAgent:
    def run(self, target):
        # Simulate social engineering attempts
        attempts = [
            "Phishing email campaign",
            "Pretexting phone call to IT support",
            "Tailgating attempt at main entrance"
        ]
        return f"Social engineering simulations for {target}: {', '.join(attempts)}"

coordinator.add_agent(SocialEngineeringAgent())\