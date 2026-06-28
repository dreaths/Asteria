import sqlite3
import pytest
from app.data.database import create_schema
from app.data.event_repository import EventRepository
from app.data.models import Event


@pytest.fixture
def repo():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_schema(conn)
    return EventRepository(conn=conn)


def test_add_and_retrieve(repo):
    event = Event(title="Dentist", date="2026-07-01", time="09:00",
                  notes=None, remind_mins=15)
    repo.add_event(event)

    results = repo.get_events_for_date("2026-07-01")

    assert len(results) == 1
    assert results[0].title == "Dentist"
    assert results[0].time == "09:00"


def test_empty_date_returns_nothing(repo):
    results = repo.get_events_for_date("2026-01-01")

    assert results == []


def test_delete_event(repo):
    event = Event(title="Meeting", date="2026-07-02", time="10:00",
                  notes=None, remind_mins=15)
    event_id = repo.add_event(event)
    repo.delete_event(event_id)

    results = repo.get_events_for_date("2026-07-02")
    assert results == []


def test_get_all_event_dates(repo):
    repo.add_event(Event(title="A", date="2026-07-01", time="09:00",
                         notes=None, remind_mins=15))
    repo.add_event(Event(title="B", date="2026-07-03", time="10:00",
                         notes=None, remind_mins=15))
    repo.add_event(Event(title="C", date="2026-07-01", time="11:00",
                         notes=None, remind_mins=15))  # same date as A

    dates = repo.get_all_event_dates()

    assert dates == {"2026-07-01", "2026-07-03"}  # duplicates collapsed


def test_mark_notified(repo):
    event_id = repo.add_event(Event(title="Standup", date="2026-07-01",
                                    time="09:00", notes=None, remind_mins=5))
    repo.mark_notified(event_id)

    # after marking, get_due_reminders should not return it again
    due = repo.get_due_reminders("2026-07-01 08:55", "2026-07-01 08:56")
    assert all(e.id != event_id for e in due)


def test_multiple_events_same_date_ordered_by_time(repo):
    repo.add_event(Event(title="Late",  date="2026-07-01", time="14:00",
                         notes=None, remind_mins=15))
    repo.add_event(Event(title="Early", date="2026-07-01", time="08:00",
                         notes=None, remind_mins=15))

    results = repo.get_events_for_date("2026-07-01")

    assert results[0].title == "Early"
    assert results[1].title == "Late"