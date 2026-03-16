from agent.agent import run_agent

query = input("Enter your travel question: ")

response = run_agent(query)

print("\nAI Sustainability Plan:\n")

print(response)