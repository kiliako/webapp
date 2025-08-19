import queue
from typing import Any, Dict, List, Optional

class AppState:
    def __init__(self):
        self.connected: bool = False
        self.msg_queue: Optional[queue.Queue] = None
        self.md_count: int = 0
        self.subscribed_set: set[str] = set()
        self.subscribed_order: List[str] = []
        self.md: Dict[str, Dict[str, Any]] = {}
        self.saved_calls: List[str] = []
        self.saved_puts: List[str] = []

STATE = AppState()
