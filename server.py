"""Campus study-room MCP server: exactly three tools."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Literal

from fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("Campus Study Rooms")
ROOMS = {
    "LIB-101": {"building": "Library", "capacity": 2, "features": ["whiteboard"]},
    "LIB-204": {"building": "Library", "capacity": 4, "features": ["whiteboard", "screen"]},
    "ENG-310": {"building": "Engineering", "capacity": 6, "features": ["screen"]},
}
SLOTS = ("09:00", "11:00", "13:00", "15:00")


class RoomInfo(BaseModel):
    room_id: str
    building: str
    capacity: int
    features: list[str]
    available_slots: list[str]


class Reservation(BaseModel):
    reservation_id: int
    room_id: str
    slot: str
    student: str
    status: Literal["reserved"] = "reserved"


def database_path() -> Path:
    return Path(os.environ.get("C5_DB_PATH", Path(__file__).with_name("reservations.db")))


def connection() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE IF NOT EXISTS reservations (id INTEGER PRIMARY KEY, room_id TEXT NOT NULL, slot TEXT NOT NULL, student TEXT NOT NULL, UNIQUE(room_id, slot))")
    return db


def lookup_room_impl(room_id: str) -> RoomInfo:
    """Read one room and its current open slots without changing reservations."""
    key = room_id.strip().upper()
    if key not in ROOMS:
        raise ValueError(f"Unknown room '{room_id}'. Choose one of: {', '.join(ROOMS)}")
    with connection() as db:
        taken = {row[0] for row in db.execute("SELECT slot FROM reservations WHERE room_id = ?", (key,))}
    return RoomInfo(room_id=key, **ROOMS[key], available_slots=[slot for slot in SLOTS if slot not in taken])


def reserve_room_impl(room_id: str, slot: str, student: str) -> Reservation:
    """Reserve one known room and time slot for one named student."""
    key = room_id.strip().upper()
    name = student.strip()
    if key not in ROOMS:
        raise ValueError(f"Unknown room '{room_id}'. Choose one of: {', '.join(ROOMS)}")
    if slot not in SLOTS:
        raise ValueError(f"Invalid slot '{slot}'. Choose one of: {', '.join(SLOTS)}")
    if not name:
        raise ValueError("Student name cannot be empty")
    try:
        with connection() as db:
            cursor = db.execute("INSERT INTO reservations(room_id, slot, student) VALUES (?, ?, ?)", (key, slot, name))
            return Reservation(reservation_id=cursor.lastrowid, room_id=key, slot=slot, student=name)
    except sqlite3.IntegrityError as exc:
        raise ValueError(f"Room {key} is already reserved at {slot}") from exc


@mcp.tool
def lookup_room(room_id: str = Field(description="Room code, for example LIB-204")) -> RoomInfo:
    """DATA: Look up one campus study room and its available two-hour start slots."""
    return lookup_room_impl(room_id)


@mcp.tool
def reserve_room(room_id: str, slot: str, student: str) -> Reservation:
    """ACTION: Create one persistent study-room reservation for a student."""
    return reserve_room_impl(room_id, slot, student)


def plan_study_session_impl(room_id: str, student: str) -> Reservation:
    """Look up a room, then reserve its earliest available slot."""
    room = lookup_room_impl(room_id)
    if not room.available_slots:
        raise ValueError(f"Room {room.room_id} has no available slots")
    return reserve_room_impl(room.room_id, room.available_slots[0], student)


@mcp.tool
def plan_study_session(room_id: str, student: str) -> Reservation:
    """ORCHESTRATION: Look up a room, then reserve its earliest available slot."""
    return plan_study_session_impl(room_id, student)


if __name__ == "__main__":
    mcp.run(transport="stdio")
