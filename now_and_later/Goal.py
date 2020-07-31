"""An implementation for the goal class."""

from datetime import datetime, timedelta
from durations import Duration
from enum import Enum
from typing import Optional


class Goal:
    """Keeps track of the state of one goal."""

    class State(Enum):
        NEW = 0
        WAITING = 1
        READY = 2
        ACTIVE = 3

    class StateError(Exception):
        pass

    def __init__(
            self,
            name: str,
            frequency: str,
            last_action: Optional[datetime] = None,
            next_action: Optional[datetime] = None,
            state: State = State.NEW,
    ):
        """
        Create a Goal object.

        This can either be used to create a new goal
        or load in existing goals.

        :param name: The name of the goal
        :param frequency: A string of the frequency
        :param last_action: The datetime of the last action
        :param next_action: The datetime of the next action to be performed
        :param state: The current state of the goal
        """
        frequency_ = Duration(frequency)
        if frequency_.to_seconds() == 0:
            raise ValueError(
                (
                    "frequency '{}' is not able to be successfully parsed or "
                    "must be a positive value"
                ).format(frequency_.representation)
            )
        if state is self.State.NEW:
            if last_action:
                raise self.StateError(
                    "Shouldn't have a last action for a new goal")
            if next_action is None:
                next_action = datetime.now() + timedelta(
                    seconds=frequency_.to_seconds())

        self._name = name
        self._frequency: Duration = frequency_
        self._last_action = last_action
        self._next_action = next_action
        self._state = state

    @property
    def next_action(self) -> datetime:
        """Get the datetime for the next action."""
        return self._next_action

    def is_ready(self) -> bool:
        """Check if the current time is after the next action's datetime."""
        return datetime.now() >= self._next_action
