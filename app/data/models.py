from dataclasses import dataclass
from typing import Optional

@dataclass
class Event:
    title: str
    date: str
    time: Optional[str]     # "14:30", or None for all day events
    notes: Optional[str]    
    remind_mins: int = 0
    is_priority: bool = False
    is_done: bool = False
    id: Optional[int] = None        # None until saved to DB, where SQLite will assign it
    notified: bool = False
    is_silent: bool = False
    is_checklist: bool = False