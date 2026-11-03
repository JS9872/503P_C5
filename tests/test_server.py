import pytest

from server import lookup_room_impl, reserve_room_impl, SLOTS


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    monkeypatch.setenv("C5_DB_PATH", str(tmp_path / "test.db"))


def test_lookup_is_read_only():
    first = lookup_room_impl("lib-204")
    second = lookup_room_impl("LIB-204")
    assert first == second
    assert first.available_slots == list(SLOTS)


def test_reservation_persists_and_blocks_duplicate():
    reservation = reserve_room_impl("LIB-204", "09:00", "Joey")
    assert reservation.reservation_id > 0
    assert "09:00" not in lookup_room_impl("LIB-204").available_slots
    with pytest.raises(ValueError, match="already reserved"):
        reserve_room_impl("LIB-204", "09:00", "Other")


def test_orchestration_calls_lookup_then_reserve(monkeypatch):
    from server import plan_study_session_impl

    calls = []
    original_lookup = lookup_room_impl
    original_reserve = reserve_room_impl
    monkeypatch.setattr("server.lookup_room_impl", lambda room: (calls.append("lookup"), original_lookup(room))[1])
    monkeypatch.setattr("server.reserve_room_impl", lambda room, slot, student: (calls.append("reserve"), original_reserve(room, slot, student))[1])
    result = plan_study_session_impl("ENG-310", "Joey")
    assert result.slot == "09:00"
    assert calls == ["lookup", "reserve"]


@pytest.mark.parametrize("room", ["", "LIB-999"])
def test_unknown_room(room):
    with pytest.raises(ValueError, match="Unknown room"):
        lookup_room_impl(room)


def test_invalid_slot_and_student():
    with pytest.raises(ValueError, match="Invalid slot"):
        reserve_room_impl("LIB-101", "10:00", "Joey")
    with pytest.raises(ValueError, match="Student name"):
        reserve_room_impl("LIB-101", "09:00", " ")
