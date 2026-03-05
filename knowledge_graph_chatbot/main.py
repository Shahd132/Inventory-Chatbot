import os
from dotenv import load_dotenv
from kg_agent.agent import run_agent, db

load_dotenv()

def main():
    print("=" * 55)
    print("    Interactive AI Knowledge Graph Agent (Neo4j)   ")
    print("=" * 55)
    print("You can add, search, edit, or delete facts.")
    print("Type 'exit' or 'quit' to stop.\n")

    if not db.verify_connection():
        print(" Could not connect to Neo4j")
        return

    history = [] 
    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "bye"):
                print("\nBot: Goodbye! Knowledge graph session ended.\n")
                db.close()
                break
            print("Thinking...")    
            response, history = run_agent(user_input, history)
            print(f"\nBot: {response}\n")

        except KeyboardInterrupt:
            print("\n\nBot: Session interrupted. Goodbye! \n")
            db.close()
            break

        except Exception as e:
            print(f"\nUnexpected error: {e}\n")
            continue

if __name__ == "__main__":
    main()

