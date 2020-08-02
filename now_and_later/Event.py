from datetime import datetime
from typing import Callable, Optional


class Event:
    def __init__(
            self,
            name: str,
            last: Optional[datetime] = None,
            next_: Optional[datetime] = None,
            callback: Optional[Callable] = None,
    ):
        self._name = name
        self._last = last
        self._next = next_
        if callback is None:
            callback = self._default_callback
        self._callback = callback

    def _default_callback(self):
        print(f"Running event in '{self.name}'")

    @property
    def name(self):
        return self._name

    @property
    def last(self):
        return self._last

    @property
    def next(self):
        return self._next

    def set_last(self, value: datetime):
        self._last = value

    def set_next(self, value: datetime):
        self._next = value

    def is_ready(self):
        if self._next is None:
            raise ValueError("_next is not set")
        return datetime.now() > self._next

    def run(self):
        if not self.is_ready():
            raise ValueError("Not ready to run")
        return self._callback()
