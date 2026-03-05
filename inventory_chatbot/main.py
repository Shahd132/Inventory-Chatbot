import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent.graph import app

load_dotenv()

def main():
    print("=" * 50)
    print("        Inventory Chatbot (SQL)              ")
    print("=" * 50)
    print("Ask me anything about assets, vendors,")
    print("locations, orders, or inventory levels.")
    print("Type 'exit' or 'quit' to stop.\n")

    config = {"configurable": {"thread_id": "inventory-session-1"}}

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
                print("\n Bot: Goodbye! Have a great day\n")
                break

            initial_state = {
                "messages":       [HumanMessage(content=user_input)],
                "question":       user_input,
                "intent":         None,
                "sql_query":      None,
                "sql_result":     None,
                "error":          None,
                "revision_count": 0
            }

            print("Thinking...\n") 
            app.invoke(initial_state, config=config)

        except KeyboardInterrupt:
            print("\n\n Bot: Session interrupted. Goodbye\n")
            break

        except Exception as e:
            print(f"\n  Unexpected error: {e}\n")
            continue


if __name__ == "__main__":
    main()