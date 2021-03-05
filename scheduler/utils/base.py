import requests
import json
import time
import datetime


VALID_BOOLEANS = ["True", "False"]
VALID_CONNECTORS = ["GT", "LT", "EQ", "GE", "LE", "BT"]
 
SENSOR_TEMPLATE = "{sensor_type}-{sensor_id}-{sensor_metric}"

ACTION_TEMPLATE = "{action_type}-{action_id}-{action_mode}"

SENSOR_URL_TEMPLATE = "http://localhost:5000/sensors/{sensor_type}/{sensor_id}"

ACTION_URL_TEMPLATE = "http://localhost:5000/actions/{action_type}/{action_id}"


def run(conditions, actions_dict, work_time, sleep_time, teardown_action):
    rule_value = _parse_conditions(conditions)
    print(f"RULE VALUE: {rule_value}")
    action_template = json.loads(actions_dict)[rule_value]
    print(f"ACTION TEMPLATE: {action_template}")
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
    print("parse")
    print(conditions)
    for condition in json.loads(conditions):
        splitted = condition.split("-")
        print("splited ", splitted )
        if len(splitted) == 1:
            print(splitted)
            if splitted[0] == "True":
                condition = True
            else:
                condition = False
            result.append(condition)
        if len(splitted) == 3:
            target_metric, connector, target_value = splitted[2].split("_")
            print("splitted 3")
            print("target_metric, connector, target_value")
            print(target_metric, connector, target_value)
            if connector in VALID_CONNECTORS:
                print("Sensor condition!")
                sensor_type = splitted[0]
                sensor_id = splitted[1]
                print(f"{sensor_type}, {sensor_id}, {target_metric}, {connector}, {target_value}")
                sensor_value = _get_sensor_value(sensor_type, sensor_id, target_metric)
                print("SENSOR VALUE")
                print(sensor_value)
                evaluated_condition = _evaluate_condition(sensor_type, sensor_value, connector, target_value, target_metric)
                result.append(evaluated_condition)
    if all(result):
        return "True"
    else:
        return "False"


def _evaluate_condition(sensor_type, sensor_value, connector, target_value, target_metric):
    print(f"sensor type {sensor_type}")
    print(f"sensor value {sensor_value}")
    print(f"sensor Connector {connector}")
    print(f"Target value {target_value}")
    print(f"Target_metrick {target_metric}")

    if sensor_type == "Clock":
        print("EVALUATES CLOCK")
        return _evaluate_dates(sensor_value, connector, target_value, target_metric)
    else:
        print("EVALUATES NUM")
        return _evaluate_num(sensor_value, connector, target_value)


def _evaluate_dates(sensor_value, connector, target_value, target_metric):
    if connector == "BT" and target_metric == "H":
        print("EVALUATEE BT")
        start, end = target_value.split(".")
        start_date = datetime.time(hour=int(start))
        end_date = datetime.time(hour=int(end))
        sensor_date = datetime.time(hour=int(sensor_value))
        print(start_date, end_date, sensor_date)
        return _between_dates(start_date, end_date, sensor_date)

    if target_metric == "H": target_date = datetime.time(hour=int(target_value)); sensor_date = datetime.time(hour=int(sensor_value))
    if target_metric == "M": target_date = datetime.time(minute=int(target_value)); sensor_date = datetime.time(minute=int(sensor_value))
    if target_metric == "S": target_date = datetime.time(second=int(target_value)); sensor_date = datetime.time(second=int(sensor_value))

    if connector == "GT": return sensor_date > target_date
    elif connector == "GE": return sensor_date >= target_date
    elif connector == "LT": return sensor_date < target_date
    elif connector == "LE": return sensor_date <= target_date
    elif connector == "EQ": return sensor_date == target_date


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
