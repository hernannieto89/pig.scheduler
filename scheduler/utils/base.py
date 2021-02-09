import requests
import json


VALID_BOOLEANS = ["True", "False"]
VALID_CONNECTORS = ["GT", "LT", "EQ", "GE", "LE"]
 
SENSOR_TEMPLATE = "{sensor_type}-{sensor_id}-{sensor_metric}"

ACTION_TEMPLATE = "{action_type}-{action_id}-{action_mode}"

SENSOR_URL_TEMPLATE = "http://localhost:5000/sensors/{sensor_type}/{sensor_id}"

ACTION_URL_TEMPLATE = "http://localhost:5000/actions/{action_type}/{action_id}/{action_mode}"


def run(conditions, actions_dict):
    rule_value = _parse_conditions(conditions)
    action_template = json.loads(actions_dict)[rule_value]
    _perform_action(action_template)


def _perform_action(action_template):
    action_type, action_id, action_mode = action_template.split("-")
    url = ACTION_URL_TEMPLATE.format(action_type=action_type, action_id=action_id, action_mode=action_mode)
    requests.post(url)


def _parse_conditions(conditions):
    """
    Returns True if all conditions al met. False otherwise.
    """
    result = []

    for condition in json.loads(conditions):
        splitted = condition.split("-")
        if len(splitted) == 1:
            result.append(bool(condition))
        if len(splitted) == 3 and splitted[1] in VALID_CONNECTORS:
            connector = splitted[1]
            sensor_type, sensor_id, sensor_metric = splitted[0].split("-")
            sensor_value = _get_sensor_value(sensor_type, sensor_id, sensor_metric)
            target_value = eval(splitted[2])
            evaluated_condition = _evaluate_condition(sensor_value, connector, target_value)
            result.append(evaluated_condition)
    if all(result):
        return "True"
    else:
        return "False"


def _evaluate_condition(sensor_value, connector, target_value):
    if connector == "GT": return sensor_value > target_value
    elif connector == "GE": return sensor_value >= target_value
    elif connector == "LT": return sensor_value < target_value
    elif connector == "LE": return sensor_value <= target_value
    elif connector == "EQ": return sensor_value == target_value


def _get_sensor_value(sensor_type, sensor_id, sensor_metric):
    url = SENSOR_URL_TEMPLATE.format(sensor_type=sensor_type, sensor_id=sensor_id)
    response = requests.get(url)
    return response[sensor_metric]
