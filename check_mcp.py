"""Exercise real stdio MCP discovery and calls without an API key."""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from agents.mcp import MCPServerStdio


async def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        old_path = os.environ.get("C5_DB_PATH")
        os.environ["C5_DB_PATH"] = str(Path(directory) / "demo.db")
        try:
            async with MCPServerStdio(
                name="Campus Study Rooms",
                params={"command": sys.executable, "args": [str(Path(__file__).with_name("server.py"))]},
                client_session_timeout_seconds=30,
            ) as server:
                names = {tool.name for tool in await server.list_tools()}
                assert names == {"lookup_room", "reserve_room", "plan_study_session"}, names
                for index, (name, arguments) in enumerate((
                    ("lookup_room", {"room_id": "LIB-204"}),
                    ("reserve_room", {"room_id": "LIB-204", "slot": "11:00", "student": "Joey"}),
                    ("plan_study_session", {"room_id": "ENG-310", "student": "Joey"}),
                    ("reserve_room", {"room_id": "LIB-204", "slot": "11:00", "student": "Alex"}),
                )):
                    result = await server.call_tool(name, arguments)
                    assert result.is_error == (index == 3)
                    print(name, "error=" + str(result.is_error), json.dumps([x.text for x in result.content if hasattr(x, "text")]))
        finally:
            if old_path is None:
                os.environ.pop("C5_DB_PATH", None)
            else:
                os.environ["C5_DB_PATH"] = old_path


if __name__ == "__main__":
    asyncio.run(main())
