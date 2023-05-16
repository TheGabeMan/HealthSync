"""
    All Intervals.icu modules to talk to the intervals API
    Infomation at:
    https://forum.intervals.icu/t/api-access-to-intervals-icu/609
"""

import json
import logging
import os
from datetime import datetime, timedelta

import requests
import urllib3
from dotenv import load_dotenv
from requests.models import HTTPBasicAuth

load_dotenv()

# intervals.icu API access
icu_athlete_id = os.getenv("icu_athlete_id")
icu_api_key = os.getenv("icu_api_key")
icu_api = f"https://intervals.icu/api/v1/athlete/{icu_athlete_id}"


def set_intervals_wellness(data):
    """Write wellness data to intervals"""
    urllib3.disable_warnings()
    jsondata = json.dumps(data)
    response = requests.put(
        f'{icu_api}/wellness/{data["id"]}',
        auth=HTTPBasicAuth("API_KEY", icu_api_key),
        json=jsondata,
        verify=False,
        timeout=10,
    )
    if response.status_code != 200:
        print("upload to intervals.icu failed with status code:", response.status_code)
        print(response.json())
        logging.info(
            "upload to intervals.icu failed with status code: %s", response.status_code
        )
        logging.info(response.json())
        return False
    else:
        print(f"Succesful writing weight {data['weight']} to Intervals API")
        logging.info("Succesful writing weight %s to Intervals API", data["weight"])
        return True


def get_intervals_wellness():
    """Read wellness from intervals"""
    # Get last 30 days of wellness data
    oldest = datetime.today().date() - timedelta(30)
    oldestiso = oldest.isoformat()

    newest = datetime.today().date()
    newestiso = newest.isoformat()

    url = f"{icu_api}/wellness?oldest={oldestiso}&newest={newestiso}"
    urllib3.disable_warnings()
    res = requests.get(
        url, auth=HTTPBasicAuth("API_KEY", icu_api_key), verify=False, timeout=10
    )
    if res.status_code != 200:
        print("Get info fromintervals.icu failed with status code:", res.status_code)
        print(res.json())
        logging.info(
            "Get info fromintervals.icu failed with status code: %s", res.status_code
        )
        logging.info(res.json())
    return res.json()


def set_intervals_weight(user_weight):
    """Write weight data to intervals"""
    # Write to Intervals.icu
    datetoday = (datetime.today().date()).strftime("%Y-%m-%d")
    data = {"weight": user_weight, "id": datetoday}
    # intervals_data = json.dumps(data)
    return set_intervals_wellness(data)
