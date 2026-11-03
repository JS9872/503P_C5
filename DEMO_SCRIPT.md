# 5–7 minute screencast guide

1. **0:00–0:45** Introduce the campus study-room assistant. Point to `server.py` and name the Data (`lookup_room`), Action (`reserve_room`), and Orchestration (`plan_study_session`) tools.
2. **0:45–1:30** Explain host/client/server: `agent.py` is the OpenAI Agents SDK host; `MCPServerStdio` is the client; `server.py` runs as a separate FastMCP process. Show the printed tool list.
3. **1:30–2:15** Run `py -m pytest -q`. Show the tests for lookup, persistent reservation, duplicate error, and orchestration order.
4. **2:15–4:30** Run `py agent.py`. Ask: “What slots are available in LIB-204?” Then “Reserve LIB-204 at 11:00 for Joey.” Then “Plan the earliest study session in ENG-310 for Joey.” Point to reservation IDs and ask for availability again to show persistence.
5. **4:30–5:15** Ask: “Reserve LIB-204 at 11:00 for Alex.” Explain the explicit duplicate error. Optionally ask about an unknown room.
6. **5:15–6:30** Explain why the tools are separated, show `READING_SUMMARY.md` and `REFLECTION.md`, and show the GitHub repository URL. Mention that the catalog is fixed for a reproducible demo.

Record your own screen and voice, then upload the 5–7 minute video and submit its URL alongside the repository URL. Reset demo reservations by deleting `reservations.db` before recording if you have run the sample prompts already.
