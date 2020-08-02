"""Keep track of when a function is called and should be called next."""
from datetime import datetime
import logging
from typing import Any, Callable, Optional


class Event:
    """A class for keeping track of when a function is called."""

    def __init__(
            self,
            name: str,
            last: Optional[datetime] = None,
            next_: Optional[datetime] = None,
            callback: Optional[Callable] = None,
    ):
        """
        Construct an event object.

        :param name: The name of the event.
        :param last: The datetime when the event last ran.
        :param next_:  The datetime when the event should run after.
        :param callback: The function that runs for the event.
        """
        self._name = name
        self._last = last
        self._next = next_
        if callback is None:
            callback = self._default_callback
        self._callback = callback

    def _default_callback(self):
        logging.info(f"Running callback in '{self.name}' event")

    @property
    def name(self):
        """Get the event's name."""
        return self._name

    @property
    def last(self):
        """Get the datetime for the last run."""
        return self._last

    @property
    def next(self) -> datetime:
        """Get the datetime when run should be available after."""
        return self._next

    def set_last(self, value: datetime) -> None:
        """Set the datetime for the last run."""
        self._last = value

    def set_next(self, value: datetime) -> None:
        """Set the datetime when run should be available after."""
        self._next = value

    def is_ready(self) -> bool:
        """Return true if it is past the next datetime."""
        if self._next is None:
            raise ValueError("_next is not set")
        return datetime.now() > self._next

    def run(self) -> Any:
        """Run the callback function if it is ready."""
        if not self.is_ready():
            raise ValueError("Not ready to run")
        return self._callback()
