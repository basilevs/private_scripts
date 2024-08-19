from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple


class StateDurationTracker:
    def __init__(self):
        self.monitoring_start: Optional[datetime] = None
        self.current_state: Optional[str] = None
        self.last_change: datetime = datetime.now()
        self.states: Dict[str, timedelta] = defaultdict(timedelta)

    def change(self, state: str) -> Tuple[str, timedelta]:
        current_state = self.current_state
        if state == current_state:
            return None
        now = datetime.now()
        elapsed = now - self.last_change
        self.last_change = now
        if current_state:
            self.states[current_state] += elapsed
        else:
            self.monitoring_start = now
        self.current_state = state
        return (current_state, elapsed)

    def ratio(self, state: str) -> float:
        if not self.monitoring_start:
            return 0.0
        return self.states[state] / (datetime.now() - self.monitoring_start)


def filter_repeats(f):
    last_args = None
    last_kwargs = None
    last_result = None

    def wrapper(*args, **kwargs):
        nonlocal last_args, last_kwargs, last_result
        # If arguments are the same as the previous invocation, return the cached result
        if (args, kwargs) == (last_args, last_kwargs):
            return last_result
        # Otherwise, call the function and update the cache
        last_args, last_kwargs = args, kwargs
        last_result = f(*args, **kwargs)
        return last_result

    return wrapper