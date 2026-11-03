# Campus Study Rooms MCP toolkit

Assignment C5 implementation. Exactly three FastMCP tools:

| Category | Tool | Input | Output / effect |
| --- | --- | --- | --- |
| Data | `lookup_room` | `room_id: str` | `RoomInfo` with open slots; no write |
| Action | `reserve_room` | `room_id`, `slot`, `student` | `Reservation` with ID; SQLite write |
| Orchestration | `plan_study_session` | `room_id`, `student` | Looks up then reserves earliest open slot |

Known rooms: `LIB-101`, `LIB-204`, `ENG-310`. Start slots: `09:00`, `11:00`, `13:00`, `15:00`. Each slot is a two-hour session. The catalog is demo data, not a real campus schedule.

## Setup (PowerShell)

```powershell
cd 'C:\Main\School\CSE FALL 4\EECE 503P\HW\C5\Code'
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Open .env and replace your-api-key-here with your own API key.
python agent.py
```

An OpenAI API key is needed for live model calls. The agent loads `.env` automatically, and `.gitignore` excludes it from Git. You can instead set `$env:OPENAI_API_KEY` in PowerShell for the current session. Set `OPENAI_MODEL` to override the default `gpt-4.1-mini`. The server runs automatically as a stdio subprocess of the agent. Reservations persist in `reservations.db`; set `C5_DB_PATH` to use another location.

## Verify and demo

```powershell
python -m pytest -q
python check_mcp.py
python agent.py
```

`check_mcp.py` exercises discovery and all three tools over a real MCP stdio connection without an API key. Try these prompts in the agent: “What slots are available in LIB-204?”, “Reserve LIB-204 at 11:00 for Joey”, “Plan the earliest study session in ENG-310 for Joey”, then repeat the reservation to show the duplicate error. The terminal prints the three discovered MCP tools. See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for a timed recording outline.

Unknown room IDs, invalid slots, blank student names, full rooms, and duplicate reservations return explicit errors. SQLite enforces one reservation per room and slot even if two writes race. Delete `reservations.db` to reset demo data.

## Submission files

- [READING_SUMMARY.md](READING_SUMMARY.md): 300–400 word article and Fetch server review.
- [REFLECTION.md](REFLECTION.md): tool boundaries and next steps.
- `server.py`, `agent.py`, and `tests/`: implementation and tests.
- Screencast: record and upload separately; include its URL in the course submission.

Repository: https://github.com/JS9872/503P_C5
