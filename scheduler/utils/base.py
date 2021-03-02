import requests
import json
import time
import datetime

VALID_BOOLEANS = ["True", "False"]
VALID_CONNECTORS = ["GT", "LT", "EQ", "GE", "LE"]
 
SENSOR_TEMPLATE = "{sensor_type}-{sensor_id}-{sensor_metric}"

ACTION_TEMPLATE = "{action_type}-{action_id}-{action_mode}"

SENSOR_URL_TEMPLATE = "http://localhost:5000/sensors/{sensor_type}/{sensor_id}"

ACTION_URL_TEMPLATE = "http://localhost:5000/actions/{action_type}/{action_id}"


def run(conditions, actions_dict, work_time, sleep_time, teardown_action):
    rule_value = _parse_conditions(conditions)
    action_template = json.loads(actions_dict)[rule_value]
    _perform_action(action_template)
    if rule_value == "True" and work_time:
        time.sleep(int(work_time))
        _perform_action(teardown_action)
        time.sleep(int(sleep_time))


def teardown_relays(relays_used):
    for relay in json.loads(relays_used):
        _perform_action("Relay-{}-LOW".format(relay))


def _perform_action(action_template):
    action_type, action_id, action_mode = action_template.split("-")
    url = ACTION_URL_TEMPLATE.format(action_type=action_type, action_id=action_id)
    requests.post(url, data={"action_mode" : action_mode})


def _parse_conditions(conditions):
    """
    Returns True if all conditions al met. False otherwise.
    """
    result = []

    for condition in json.loads(conditions):
        splitted = condition.split("-")
        if len(splitted) == 1:
            result.append(bool(condition))
        if len(splitted) == 3:
            target_metric, connector, target_value = splitted[2].split("_")
            if connector in VALID_CONNECTORS:
                print("Sensor condition!")
                sensor_type = splitted[0]
                sensor_id = splitted[1]
                print(sensor_type, sensor_id, target_metric, connector, target_value)
                sensor_value = _get_sensor_value(sensor_type, sensor_id, target_metric)
                evaluated_condition = _evaluate_condition(sensor_type, sensor_value, connector, target_value, target_metric)
                result.append(evaluated_condition)
    if all(result):
        return "True"
    else:
        return "False"


def _evaluate_condition(sensor_type, sensor_value, connector, target_value, target_metric):
    if sensor_type == "Clock":
        return _evaluate_dates(sensor_value, connector, target_value, target_metric)
    else:
        return _evaluate_num(sensor_value, connector, target_value)


def _evaluate_dates(sensor_value, connector, target_value, target_metric):

    if connector == "BT" and target_metric == "H":
        start, end = target_value.split(".")
        if target_metric == "H": start_date = {"hour": int(start)}; end_date = {"hour":  int(end)}; sensor_date = {"hour":  int(sensor_value)}
        if target_metric == "M": start_date = {"minute":  int(start)}; end_date = {"minute":  int(end)}; sensor_date = {"minute":  int(sensor_value)}
        if target_metric == "S": start_date = {"second":  int(start)}; end_date = {"second":  int(end)}; sensor_date = {"second":  int(sensor_value)}
        return _between_dates(datetime.time(**start_date), datetime.time(**end_date), datetime.time(**sensor_date))

    if target_metric == "H": target_date = {"hour": int(target_value)}; sensor_date = {"hour": int(sensor_value)}
    if target_metric == "M": target_date = {"minute": int(target_value)}; sensor_date = {"minute": int(sensor_value)}
    if target_metric == "S": target_date = {"second": int(target_value)}; sensor_date = {"second": int(sensor_value)}

    if connector == "GT": return datetime.time(**sensor_date) > datetime.time(**target_date)
    elif connector == "GE": return datetime.time(**sensor_date) >= datetime.time(**target_date)
    elif connector == "LT": return datetime.time(**sensor_date) < datetime.time(**target_date)
    elif connector == "LE": return datetime.time(**sensor_date) <= datetime.time(**target_date)
    elif connector == "EQ": return datetime.time(**sensor_date) == datetime.time(**target_date)


def _evaluate_num(sensor_value, connector, target_value):
    if connector == "GT": return float(sensor_value) > float(target_value)
    elif connector == "GE": return float(sensor_value) >= float(target_value)
    elif connector == "LT": return float(sensor_value) < float(target_value)
    elif connector == "LE": return float(sensor_value) <= float(target_value)
    elif connector == "EQ": return float(sensor_value) == float(target_value)


def _get_sensor_value(sensor_type, sensor_id, sensor_metric):
    url = SENSOR_URL_TEMPLATE.format(sensor_type=sensor_type, sensor_id=sensor_id)
    response = requests.get(url).json()
    return response[sensor_metric]


def _between_dates(start_date, end_date, value_date):
    if start_date < end_date:
        return value_date >= start_date and value_date <= end_date
    else: # crosses midnight
        return value_date >= start_date or value_date <= end_date
