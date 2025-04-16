import datetime
import requests

def get_start_time():
    now = datetime.datetime.now()
    start_of_day = datetime.datetime(now.year, now.month, now.day, 0,0,0 )
    start_time = int(start_of_day.timestamp() * 1000)
    return start_time

def get_google_fit_water_intake(access_token):
    end_time = int(datetime.datetime.now().timestamp() * 1000)
    start_time = get_start_time()

    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
    headers = {"Authorization": f"Bearer {access_token}"}
    body = {
        "aggregateBy": [{"dataTypeName": "com.google.hydration"}],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start_time,
        "endTimeMillis": end_time,
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    water = [v["fpVal"] for v in data["bucket"][0]["dataset"][0]["point"][0]["value"] if "fpVal" in v]
    return water


def get_google_fit_heart_rate(access_token):
    end_time = int(datetime.datetime.now().timestamp() * 1000)
    start_time = get_start_time()

    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
    headers = {"Authorization": f"Bearer {access_token}"}
    body = {
        "aggregateBy": [{"dataTypeName": "com.google.heart_rate.bpm"}],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start_time,
        "endTimeMillis": end_time,
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    heart_rate = [[v["fpVal"] for v in data["bucket"][0]["dataset"][0]["point"][0]["value"] if "fpVal" in v]]
    return heart_rate


def get_google_fit_steps(access_token):
    end_time = int(datetime.datetime.now().timestamp() * 1000)
    start_time = get_start_time()

    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
    headers = {"Authorization": f"Bearer {access_token}"}
    body = {
        "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
        "bucketByTime": {"durationMillis": 86400000},  # Theo ngày
        "startTimeMillis": start_time,
        "endTimeMillis": end_time,
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    steps = data["bucket"][0]["dataset"][0]["point"][0]["value"][0]["intVal"]
    return steps
