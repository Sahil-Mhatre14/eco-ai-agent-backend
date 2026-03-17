"""Command-line interface for the Sustainability AI Agent.

This file provides a simple interactive prompt for asking travel questions
and getting back sustainability recommendations.

Example:
  python cli.py

Or single-question mode:
  python cli.py "Travel from Las Vegas to San Jose sustainably"
"""

from agent.agent import run_agent
import sys


def main():
    # If a query is passed as an argument, use it and exit.
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip()
        if not query:
            print("Please provide a query string.")
            sys.exit(1)
        response = run_agent(query)
        print(response)
        return

    # Otherwise, run an interactive prompt.
    print("Sustainability AI Agent (CLI)")
    print("Type your travel question and press Enter. Ctrl+C to quit.")

    try:
        while True:
            query = input("\n> ").strip()
            if not query:
                print("Please type a question.")
                continue
            print("\nThinking...\n")
            response = run_agent(query)
            print(response)
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
