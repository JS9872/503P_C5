"""OpenAI Agents SDK host and MCP stdio client."""

import asyncio
import os
import sys
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv


async def main() -> None:
    load_dotenv(Path(__file__).with_name(".env"))
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY in .env or the environment before running the agent")
    server_file = Path(__file__).with_name("server.py")
    async with MCPServerStdio(
        name="Campus Study Rooms",
        params={"command": sys.executable, "args": [str(server_file)]},
        client_session_timeout_seconds=30,
    ) as server:
        tools = await server.list_tools()
        print("MCP tools:", ", ".join(tool.name for tool in tools))
        agent = Agent(
            name="Campus Study Assistant",
            model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=(
                "Use the campus MCP tools for all room facts and reservations. "
                "Use lookup_room for availability, reserve_room for a specified slot, "
                "and plan_study_session when asked for the earliest open slot. "
                "Never claim a reservation succeeded unless the tool returned a reservation ID. "
                "For known rooms use LIB-101, LIB-204, or ENG-310. "
                "Explain tool errors clearly."
            ),
            mcp_servers=[server],
        )
        print("Enter a request (or 'quit').")
        while True:
            try:
                prompt = input("You> ").strip()
            except EOFError:
                break
            if prompt.lower() in {"quit", "exit"}:
                break
            if prompt:
                result = await Runner.run(agent, prompt)
                print("Agent>", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
