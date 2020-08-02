from datetime import datetime, timedelta
from now_and_later.Goal import Goal
from operator import attrgetter
from typing import List, Optional


class Scheduler:

    def __init__(self):
        self._goals: List[Goal] = []

    def plan(
            self,
            duration: timedelta = timedelta(weeks=1),
            step: timedelta = timedelta(days=1),
    ):
        datetimes = self.get_datetime_range(duration, step)
        goals: List[Optional[List[Goal]]] = []
        for dt in datetimes:
            goals.append(self._prioritize_goals(dt))

    @staticmethod
    def get_datetime_range(duration, step):
        start_time = datetime.now()
        end_time = start_time + duration
        dt = start_time
        datetimes: List[datetime] = [dt]
        while dt < end_time:
            dt = dt + step
            datetimes.append(dt)
        return datetimes

    def add_goal(self, goal: Goal):
        self._goals.append(goal)

    def add_goals(self, *goals: List[Goal]):
        for g in goals:
            self.add_goal(g)

    def _prioritize_goals(self, dt: datetime):
        goals = self._get_main_actions_on_datetime(dt)
        sorted_goals = sorted(goals, key=attrgetter('priority'), reverse=True)
        for g in sorted_goals:
            print(f"{g.name}: {g.priority}")

    def _get_main_actions_on_datetime(self, dt: datetime):
        out_goals: List[Goal] = []
        for g in self._goals:
            if dt > g.next_main_action:
                out_goals.append(g)
        return out_goals


if __name__ == '__main__':
    from freezegun import freeze_time

    with freeze_time(datetime(2020, 1, 1)):

        call_mom_goal = Goal('Call Mom', timedelta(days=1), 3)
        call_dad_goal = Goal('Call Dad', timedelta(days=1), 2)
        call_sister_goal = Goal('Call Heather', timedelta(days=1), 2.5)

        scheduler = Scheduler()
        scheduler.add_goals(call_dad_goal, call_mom_goal, call_sister_goal)
        scheduler._prioritize_goals(datetime(2020, 1, 3))
