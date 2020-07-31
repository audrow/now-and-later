from now_and_later.Goal import Goal
from datetime import date, datetime
import freezegun
import pytest


@freezegun.freeze_time('2020-01-01')
@pytest.mark.parametrize("frequency, expected_date", [
    ('1 day', date(2020, 1, 2)),
    ('1 week', date(2020, 1, 8)),
    ('2 weeks', date(2020, 1, 15)),
    ('1 month', date(2020, 1, 31)),
    ('3 months', date(2020, 4, 1)),
    ('6 months', date(2020, 7, 2)),
    ('1 year', date(2021, 1, 1)),
])
def test_set_initial_action_from_frequency(
        frequency: str, expected_date: date):
    goal = Goal('my goal', frequency)
    assert goal.next_action.date() == expected_date


def test_new_state_with_last_action_date():
    with pytest.raises(Goal.StateError):
        Goal('my goal', '1 day',
             last_action=datetime.now(), state=Goal.State.NEW)


@pytest.mark.parametrize("test_date, expected_result", [
    (date(2020, 1, 1), False),
    (date(2020, 1, 6), False),
    (date(2020, 1, 7), False),
    (date(2020, 1, 8), True),
    (date(2020, 1, 9), True),
])
def test_is_ready(test_date, expected_result):
    with freezegun.freeze_time('2020-01-01'):
        goal = Goal('my goal', '1 week')
    with freezegun.freeze_time(test_date):
        assert goal.is_ready() == expected_result


@pytest.mark.parametrize("frequency", [
    '',
    'foo',
    'weekly',
    'monthly',
])
def test_bad_frequency_input(frequency):
    with pytest.raises(ValueError):
        Goal('My goal', frequency)
