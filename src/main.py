import asyncio
import os
from dotenv import load_dotenv

# Load environment variables before importing ADK components
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from src.agents.definitions import cio_agent

APP_NAME = "market_interpreter"
USER_ID = "portfolio_manager"
SESSION_ID = "daily_cycle_001"

async def main():
    print("--- Initializing The Market Interpreter ---")
    
    # 1. Setup Session Service
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, 
        user_id=USER_ID, 
        session_id=SESSION_ID
    )
    print(f"Session created: {SESSION_ID}")

    # 2. Setup Runner with CIO Agent
    runner = Runner(
        agent=cio_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner initialized with Root Agent: {cio_agent.name}")

    # 3. Trigger the Daily Cycle
    query = "Run Daily Cycle"
    print(f"\n>>> User Query: {query}\n")

    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    try:
        events = runner.run_async(
            user_id=USER_ID, 
            session_id=SESSION_ID, 
            new_message=content
        )

        async for event in events:
            # We can inspect events here if we want to see the thought process (streaming)
            # or just wait for the final response.
            if event.is_final_response():
                final_response = event.content.parts[0].text
                print("\n=== CIO FINAL REPORT ===\n")
                print(final_response)
                print("\n========================\n")
            elif hasattr(event, 'content') and event.content and event.content.parts:
                 # Optional: Print intermediate thoughts or tool calls if desired
                 print(event.content.parts[0].text)
                 
                 
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
