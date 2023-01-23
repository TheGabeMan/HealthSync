"""
    All Intervals.icu modules to talk to the intervals API
    Infomation at: https://forum.intervals.icu/t/api-access-to-intervals-icu/609
"""

from datetime import datetime, timedelta
import json
import logging
import os
import requests
from requests.models import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

# intervals.icu API access
icu_athlete_id = os.getenv("icu_athlete_id")
icu_api_key = os.getenv("icu_api_key")
icu_api = "https://intervals.icu/api/v1/athlete/%s" % icu_athlete_id


def set_intervals_wellness(data):
    requests.packages.urllib3.disable_warnings()
    res = requests.put(
        "%s/wellness/%s" % (icu_api, data["id"]),
        auth=HTTPBasicAuth("API_KEY", icu_api_key),
        json=data,
        verify=False,
    )
    if res.status_code != 200:
        print("upload to intervals.icu failed with status code:",
              res.status_code)
        print(res.json())
        logging.info("upload to intervals.icu failed with status code:",
                     res.status_code)
        logging.info(res.json())
    else:
        print("Succesful writing weight to intervals.icu")
        logging.info("Succesful writing weight to intervals.icu")


def get_intervals_wellness():
    # Get last 30 days of wellness data
    oldest = datetime.today().date() - timedelta(30)
    newest = datetime.today().date()
    url = "%s/wellness?oldest=%s&newest=%s" % (
        icu_api,
        oldest.isoformat(),
        newest.isoformat(),
    )
    requests.packages.urllib3.disable_warnings()
    res = requests.get(
        url,
        auth=HTTPBasicAuth("API_KEY", icu_api_key),
        verify=False,
    )
    if res.status_code != 200:
        print("Get info fromintervals.icu failed with status code:",
              res.status_code)
        print(res.json())
        logging.info("Get info fromintervals.icu failed with status code:",
                     res.status_code)
        logging.info(res.json())
    return res.json()


def set_intervals_weight(user_weight):
    # Write to Intervals.icu
    datetoday = (datetime.today().date()).strftime("%Y-%m-%d")  # format '2023-01-22'
    intervals_data = json.loads('{ "weight": "%s", "id": "%s"}' % (user_weight, datetoday))
    set_intervals_wellness(intervals_data)
