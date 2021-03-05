import pytest
import requests
import requests_mock

import datetime

from scheduler.utils.base import _parse_conditions, _evaluate_dates, _between_dates


@pytest.mark.parametrize("condition, expected", [('["True"]', "True"), ('["False"]', "False")])
def test__parse_conditions(condition, expected):
    assert _parse_conditions(condition) == expected


@pytest.mark.parametrize("start, end, current_value, expected", [(6, 2, 8, True), (6, 2, 3, False), (12, 15, 13, True)])
def test__between_dates(start, end, current_value, expected):
    start_date = datetime.time(hour=start)
    end_date = datetime.time(hour=end)
    target_date = datetime.time(hour=current_value)
    assert _between_dates(start_date, end_date, target_date) == expected


@pytest.mark.parametrize("sensor_value, connector, target_value, target_metric, expected", [("18", "BT", "2.6", "H", False), ("18", "BT", "6.2", "H", True)])
def test__evaluate_dates(sensor_value, connector, target_value, target_metric, expected):
        assert _evaluate_dates(sensor_value, connector, target_value, target_metric) == expected


@pytest.mark.parametrize("conditions, response, expected", [('["Clock-1-H_BT_2.6"]', '{"H": 18, "M": 30, "S": 30}', "False"), ('["Clock-1-H_BT_6.2"]', '{"H": 18, "M": 30, "S": 30}', "True")])
def test__parse_conditions(conditions, response, expected):
    with requests_mock.Mocker() as m:
        m.get('http://localhost:5000/sensors/Clock/1', text=response)
        assert _parse_conditions(conditions) == expected
