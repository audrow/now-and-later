from datetime import datetime, timedelta
from freezegun import freeze_time
import pytest
import pytest_mock
from transitions import MachineError

from now_and_later.Event import Event
from now_and_later.Goal import Goal


class States:
    NEW = 'new'
    IDLE = 'idle'
    ACTIVE = 'active'


def test_transitions():
    goal = Goal(
        name='goal',
        duration=timedelta(seconds=0),
        priority=1.0
    )
    assert goal.state == States.NEW
    for _ in range(5):
        goal.preempt()
        assert goal.state == States.NEW
    for _ in range(10):
        goal.act()
        assert goal.state == States.ACTIVE
        for _ in range(5):
            goal.snooze()
            assert goal.state == States.ACTIVE
        goal.complete()
        assert goal.state == States.IDLE
        for _ in range(5):
            goal.preempt()
            assert goal.state == States.IDLE


def test_bad_transitions():
    goal = Goal(
        name='goal',
        duration=timedelta(seconds=0),
        priority=1.0
    )
    assert goal.state == States.NEW
    for _ in range(10):
        with pytest.raises(MachineError):
            goal.snooze()
        with pytest.raises(MachineError):
            goal.complete()

        goal.act()
        assert goal.state == States.ACTIVE
        with pytest.raises(MachineError):
            goal.act()
        with pytest.raises(MachineError):
            goal.preempt()

        goal.complete()
        assert goal.state == States.IDLE


def test_transition_callbacks(mocker: pytest_mock.MockFixture):
    mock_preempt_fn = mocker.MagicMock()
    mock_action_fn = mocker.MagicMock()
    mock_snooze_fn = mocker.MagicMock()
    mock_completion_fn = mocker.MagicMock()

    zero_timedelta = timedelta(seconds=0)
    goal = Goal(
        name='goal',
        priority=1.0,
        duration=zero_timedelta,
        preempt_duration=zero_timedelta,
        snooze_duration=zero_timedelta,
        preempt_event=Event(
            'preempt',
            next_=datetime.now(),
            callback=mock_preempt_fn,
        ),
        action_event=Event(
            'action',
            next_=datetime.now(),
            callback=mock_action_fn,
        ),
        snooze_event=Event(
            'snooze',
            next_=datetime.now(),
            callback=mock_snooze_fn,
        ),
        completion_event=Event(
            'completion',
            next_=datetime.now(),
            callback=mock_completion_fn
        ),
    )
    assert goal.state == States.NEW
    assert not mock_preempt_fn.called
    for i in range(5):
        goal.preempt()
        assert mock_preempt_fn.call_count == i + 1
        assert goal.state == States.IDLE

    assert not mock_action_fn.called
    goal.act()
    assert mock_action_fn.called
    assert goal.state == States.ACTIVE

    assert not mock_snooze_fn.called
    for i in range(5):
        goal.snooze()
        assert mock_snooze_fn.call_count == i + 1
        assert goal.state == States.ACTIVE
    assert not mock_completion_fn.called
    goal.complete()
    assert mock_completion_fn.called
    assert goal.state == States.IDLE


def test_skip_transition_callbacks():
    zero_timedelta = timedelta(seconds=0)
    goal = Goal(
        name='goal',
        priority=1.0,
        duration=zero_timedelta,
        preempt_duration=zero_timedelta,
        snooze_duration=zero_timedelta,
    )
    assert not goal._is_preempt_ready()
    goal.preempt()
    assert goal._is_main_action_ready()
    goal.act()
    assert not goal._is_snooze_ready()
    goal.snooze()


def test_main_action_scheduling():
    with freeze_time(datetime(2020, 1, 1)):
        goal = Goal(
            name='goal',
            priority=1.0,
            duration=timedelta(days=10),
            preempt_duration=timedelta(days=2),
            snooze_duration=timedelta(days=3),
        )
        assert not goal._is_preempt_ready()
        assert not goal._is_main_action_ready()

    assert goal._action_event.next == datetime(2020, 1, 11)
    assert goal._preempt_event.next == datetime(2020, 1, 9)

    with freeze_time(datetime(2020, 1, 10)):
        assert goal._is_preempt_ready()
        goal.preempt()
        assert goal._preempt_event.last == datetime(2020, 1, 10)

    with freeze_time(datetime(2020, 1, 12)):
        assert goal._is_main_action_ready()
        goal.act()
    assert goal._action_event.last == datetime(2020, 1, 12)
    assert goal._snooze_event.next == datetime(2020, 1, 15)

    with freeze_time(datetime(2020, 1, 16)):
        assert goal._is_snooze_ready()
        goal.snooze()
    assert goal._snooze_event.last == datetime(2020, 1, 16)
    assert goal._snooze_event.next == datetime(2020, 1, 19)

    with freeze_time(datetime(2020, 1, 20)):
        goal.complete()

    assert goal._preempt_event.last == datetime(2020, 1, 10)
    assert goal._preempt_event.next == datetime(2020, 1, 28)

    assert goal._action_event.last == datetime(2020, 1, 12)
    assert goal._action_event.next == datetime(2020, 1, 30)

    assert goal._completion_event.last == datetime(2020, 1, 20)
    assert goal._completion_event.next is None


def test_no_duration_constructor():
    with pytest.raises(ValueError):
        Goal(
            name='goal',
            priority=1.0,
            duration=timedelta(days=1),
            preempt_event=Event(
                'preempt',
            ),
        )
    with pytest.raises(ValueError):
        Goal(
            name='goal',
            priority=1.0,
            duration=timedelta(days=1),
            snooze_event=Event(
                'snooze',
            ),
        )


@pytest.mark.parametrize('name', [
    'Goal',
    'Goal1',
    'MyGoal',
])
def test_name(name):
    assert Goal(
        name=name,
        priority=1.0,
        duration=timedelta(days=1)).name == name


@pytest.mark.parametrize('priority', [
    1.0,
    1,
    2,
    100,
])
def test_priority_accessors(priority):
    default_priority = 0
    g = Goal(
        name='goal', priority=default_priority, duration=timedelta(days=1))

    g.set_priority(priority)
    assert g.priority == priority

    g._reset_priority()
    assert g.priority == default_priority
