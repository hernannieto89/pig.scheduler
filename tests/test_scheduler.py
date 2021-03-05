import pytest
import datetime

from scheduler.utils.base import _parse_conditions, _evaluate_condition, _evaluate_dates, _between_dates


@pytest.mark.parametrize("condition, expected", [('["True"]', "True"), ('["False"]', "False")])
def test__parse_conditions(condition, expected):
    assert _parse_conditions(condition) == expected


@pytest.mark.parametrize("start, end, current_value, expected", [(6, 2, 8, True), (6, 2, 3, False), (12, 15, 13, True)])
def test__between_dates(start, end, current_value, expected):
    start_date = datetime.time(hour=start)
    end_date = datetime.time(hour=end)
    target_date = datetime.time(hour=current_value)
    assert _between_dates(start_date, end_date, target_date) == expected