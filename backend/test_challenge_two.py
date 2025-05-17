from backend.agents.forensic_agent_challenge2 import create_forensic_agent
from agents.extractive_qa_agent import create_extractive_agent

def main():
    agent = create_forensic_agent()

    while True:
       query = input("Enter your transaction analysis prompt (or 'exit' to quit): ")
       if query.lower() == "exit":
            break

       response = agent.invoke({"input": query})
       print("\nResponse:\n", response["output"])



if __name__ == "__main__":
    main()
