import collections
import datetime
import threading
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

@dataclass
class NetworkEvent:
    id: int
    timestamp: str
    client: str
    event_type: str
    details: str
    threat_level: str

class LiveTrafficLogger:
    def __init__(self, max_events: int = 150):
        self.max_events = max_events
        self.events: collections.deque = collections.deque(maxlen=max_events)
        self.lock = threading.Lock()
        self.counter = 0

    def log(self, client: str, event_type: str, details: str, threat_level: str = "INFO"):
        with self.lock:
            self.counter += 1
            now_str = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            event = NetworkEvent(
                id=self.counter,
                timestamp=now_str,
                client=client,
                event_type=event_type,
                details=details,
                threat_level=threat_level
            )
            self.events.append(event)

    def get_recent_events(self, limit: int = 30) -> List[Dict]:
        with self.lock:
            recent = list(self.events)[-limit:]
            recent.reverse()
            return [asdict(e) for e in recent]

    def clear(self):
        with self.lock:
            self.events.clear()

traffic_logger = LiveTrafficLogger(max_events=200)
