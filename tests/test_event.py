from datetime import datetime
import pytest
import pytest_mock
from freezegun import freeze_time

from now_and_later.Event import Event


@pytest.mark.parametrize("name, last, next_", [
    ("Node", None, None),
    ("Node2", None, None),
    ("Node", datetime(2020, 1, 1), None),
    ("Node", datetime(2020, 1, 1), datetime(2020, 1, 2)),
])
def test_properties(name, last, next_):
    event = Event(name, last, next_)
    assert name == event.name
    assert last == event.last
    assert next_ == event.next


@pytest.mark.parametrize('date', [
    datetime(2020, 1, 1),
    datetime(2020, 1, 2),
    datetime(2020, 1, 1, 1, 1, 1),
])
def test_setters(date):
    event = Event('name')

    event.set_last(date)
    assert date == event.last

    event.set_next(date)
    assert date == event.next


def test_is_ready_with_no_next():
    event = Event('name')
    with pytest.raises(ValueError):
        event.is_ready()


@freeze_time(datetime(2020, 1, 2, 9, 30))
@pytest.mark.parametrize('date, expected', [
    (datetime(1, 1, 1), True),
    (datetime(2020, 1, 1), True),
    (datetime(2020, 1, 2), True),
    (datetime(2020, 1, 2, 9), True),
    (datetime(2020, 1, 2, 10), False),
    (datetime(2020, 1, 3), False),
    (datetime(2020, 2, 1), False),
    (datetime(4000, 1, 1), False),
])
def test_callback(date, expected):
    is_run = False

    def run_it():
        nonlocal is_run
        is_run = True

    event = Event('name', next_=date, callback=run_it)
    assert expected == event.is_ready()
    if expected:
        event.run()
        assert is_run
    else:
        with pytest.raises(ValueError):
            event.run()
        assert not is_run


def test_default_callback(mocker: pytest_mock.MockFixture):
    with freeze_time(datetime(2020, 1, 1)):
        event = Event('name', next_=datetime.now())
    with freeze_time(datetime(2020, 1, 2)):
        print_ = mocker.patch('now_and_later.Event.print')
        assert not print_.called
        event.run()
        assert print_.called
