import requests


ACTION_URL_TEMPLATE = "http://localhost:5000/actions/{action_type}/{action_id}/{action_mode}"


def perform_action(action_template):
    action_type, action_id, action_mode = action_template.split("-")
    url = ACTION_URL_TEMPLATE.format(action_type=action_type, action_id=action_id, action_mode=action_mode)
    requests.post(url)
