"""An implementation of the Goal class."""

from datetime import datetime, timedelta
import logging
from transitions import Machine
from typing import Optional

from now_and_later.Event import Event


class Goal:
    """
    The `Goal` class.

    The `Goal` class uses the `transitions` for a finite state machine.
    This class has three states: new, idle, and active. The instance is
    new until the first transition occurs. Afterwards, the state alternates
    between idle and active. Idle is when waiting for the goal's main
    callback to be ready. After the goal's main callback is called, the state
    is active until the completion callback is called.
    """

    states = ['new', 'idle', 'active']

    transitions = [
        {
            'trigger': 'preempt',
            'source': ['new', 'idle'],
            'dest': 'idle',
            'conditions': '_is_preempt_ready',
            'after': '_preempt_action',
        },
        {
            'trigger': 'act',
            'source': ['new', 'idle'],
            'dest': 'active',
            'conditions': '_is_main_action_ready',
            'after': '_main_action',
        },
        {
            'trigger': 'snooze',
            'source': 'active',
            'dest': 'active',
            'conditions': '_is_snooze_ready',
            'after': '_snooze_action',
        },
        {
            'trigger': 'complete',
            'source': 'active',
            'dest': 'idle',
            'after': '_completion_action',
        },
    ]

    def __init__(
            self,
            name: str,
            duration: timedelta,
            priority: float,
            preempt_duration: Optional[timedelta] = None,
            snooze_duration: Optional[timedelta] = None,
            preempt_event: Optional[Event] = None,
            snooze_event: Optional[Event] = None,
            action_event: Optional[Event] = None,
            completion_event: Optional[Event] = None,
    ):
        """
        The constructor of the `Goal` class.

        :param name: The name of the goal.
        :param duration:
            The desired period for the goal to be completed in;
            for example, every two weeks.
        :param priority: the priority of this goal being completed.
        :param preempt_duration:
            The amount of time before the goal's main callback that
            the preemptable event's callback should be called. This
            might be a reminder to prepare something before the goal.
            For example, schedule a meeting with a friend for the goal
            of catching up with them in a few days.
        :param snooze_duration:
            The amount of time after the goal's main callback before
            the snooze callback is executed. The snooze call back
            will continue to repeat at this duration until the
            main goal is completed (the completion callback called)
        :param preempt_event:
            The event to keep track of preemtable event calls.
        :param snooze_event:
            The event to keep track of snooze event calls.
        :param action_event:
            The event to keep track of the main action event calls.
        :param completion_event:
            The event to keep track of the completion of goals event calls.
        """
        self._name = name
        self._action_duration = duration
        self._default_priority = priority
        self._priority = self._default_priority

        if preempt_duration and not preempt_event:
            preempt_event = Event('preempt')
        elif preempt_event and preempt_duration is None:
            raise ValueError("Can't have a preempt event without a duration")

        if action_event is None:
            action_event = Event('action')

        if snooze_duration and not snooze_event:
            snooze_event = Event('snooze')
        elif snooze_event and snooze_duration is None:
            raise ValueError("Can't have a snooze event without a duration")

        if completion_event is None:
            completion_event = Event('completion')

        self._preempt_duration = preempt_duration
        self._snooze_duration = snooze_duration

        self._preempt_event = preempt_event
        self._action_event = action_event
        self._snooze_event = snooze_event
        self._completion_event = completion_event

        if self._action_event.next is None:
            self.schedule_action()

        self._machine = Machine(
            model=self,
            states=Goal.states,
            transitions=Goal.transitions,
            initial=Goal.states[0],
        )

    def schedule_action(self):
        """Schedule the action and preempt events."""
        if self._completion_event.last is None:
            self._action_event.set_next(datetime.now() + self._action_duration)
        else:
            self._action_event.set_next(
                self._completion_event.last + self._action_duration)

        if self._preempt_event is not None:
            self._preempt_event.set_next(
                self._action_event.next - self._preempt_duration)
        if self._snooze_event is not None:
            self._snooze_event.set_next(None)

    def set_priority(self, value: float) -> None:
        """Set the priority of the goal."""
        self._priority = value

    @property
    def priority(self) -> float:
        """Get the priority of the goal."""
        return self._priority

    @property
    def name(self) -> str:
        """Get the name of the goal."""
        return self._name

    @property
    def next_preempt_action(self) -> Optional[datetime]:
        """Get the datetime for the next preempt action."""
        if self._preempt_event is None:
            return None
        return self._preempt_event.next

    @property
    def next_main_action(self) -> datetime:
        """Get the datetime for the next main action."""
        return self._action_event.next

    @property
    def next_snooze_action(self) -> Optional[datetime]:
        """Get the datetime for the next snooze action."""
        if self._snooze_event is None:
            return None
        return self._snooze_event.next

    def _reset_priority(self) -> None:
        logging.info(f'Priority reset to {self._default_priority}')
        self._priority = self._default_priority

    def _is_preempt_ready(self) -> bool:
        if self._preempt_event is None or self.state == 'active':
            return False
        return self._preempt_event.is_ready()

    def _is_main_action_ready(self) -> bool:
        if self.state == 'active':
            return False
        return self._action_event.is_ready()

    def _is_snooze_ready(self) -> bool:
        if self._snooze_event is None or self.state != 'active':
            return False
        return self._snooze_event.is_ready()

    def _preempt_action(self) -> None:
        self._preempt_event.run()
        self._preempt_event.set_last(datetime.now())
        self._preempt_event.set_next(None)

    def _main_action(self) -> None:
        if self._snooze_event is not None:
            self._snooze_event.set_next(datetime.now() + self._snooze_duration)

        self._action_event.run()
        self._action_event.set_last(datetime.now())
        self._action_event.set_next(None)

    def _snooze_action(self) -> None:
        self._snooze_event.run()
        self._snooze_event.set_last(datetime.now())
        self._snooze_event.set_next(datetime.now() + self._snooze_duration)

    def _completion_action(self) -> None:
        self._completion_event.execute_callback()
        self._completion_event.set_last(datetime.now())

        self.schedule_action()
        self._reset_priority()
