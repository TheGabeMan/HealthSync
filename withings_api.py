"""
    All withings modules to talk to the Withings API
    Infomation at: https://developer.withings.com/
"""

import json
import webbrowser
import os
import sys
from datetime import datetime, timedelta
# from genericpath import isfile

import requests
from dotenv import load_dotenv

load_dotenv()

# Withings API access
withings_client_id = os.getenv("withings_client_id")
withings_client_secret = os.getenv("withings_client_secret")
withings_cfg = "withings.json"
withings_redirect_uri = os.getenv("withings_redirect_uri")
withings_api = "https://wbsapi.withings.net"


def get_withings_user_weight():
    """Read user weight from withings"""
    withings_data = get_withings_data()
    user_weight = withings_data["weight"]
    return user_weight


def get_withings_data():
    """Read user data from withings API"""
    withings_access_token = (
        withings_refresh(json.load(open(withings_cfg, encoding="utf8")))
        if os.path.isfile(withings_cfg)
        else withings_authenticate()
    )
    withings_user_measurements = get_withings_last_measurement(withings_access_token)

    return withings_user_measurements


def withings_authenticate():
    ''' Get first time authentication token from withings'''
    url = 'https://account.withings.com/oauth2_user/authorize2'
    params = {'response_type': 'code',
              'client_id': withings_client_id,
              'state': 'interval',
              'scope': 'user.metrics',
              'redirect_uri': withings_redirect_uri
              }

    response = requests.get(url, params=params, timeout=10)
    webbrowser.open(response.url, new=2)
    withings_code = input("Insert the code block from the URL after authorizing: ")

    paramdata = {
        "action": "requesttoken",
        "code": withings_code,
        "client_id": withings_client_id,
        "client_secret": withings_client_secret,
        "grant_type": "authorization_code",
        "redirect_uri": withings_redirect_uri,
    }
    res = requests.post(f"{withings_api}/v2/oauth2", params=paramdata, timeout=10)
    out = res.json()
    if res.status_code == 200:
        json.dump(out["body"], open(withings_cfg, "w", encoding="utf8"))
        return out["body"]["access_token"]

    print("authentication failed:")
    print(out)
    sys.exit()


def withings_refresh(token):
    """refresh current token
    this makes sure we won't have to reauthorize again.
    """

    url = f"{withings_api}/v2/oauth2"
    res = requests.post(
        url,
        params={
            "client_id": withings_client_id,
            "client_secret": withings_client_secret,
            "action": "requesttoken",
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
        },
        timeout=10,
    )
    out = res.json()
    if out["status"] == 0:
        json.dump(out["body"], open(withings_cfg, "w", encoding="utf8"))
        return out["body"]["access_token"]
    else:
        print(out)
        sys.exit()


def get_withings_measurements(token):
    """Read data from withings"""
    start_date = datetime.today().date() - timedelta(30)  # last 30 days
    # start_date = datetime(2022,1,1)  # override to initially get all values
    url = f"{withings_api}/v2/measure"
    headers = {"Authorization": f"Bearer {token}"}

    # Getting meastypes 1,5,6,8,11,76,88 just reads all available
    # measurements from the Smart Body Analyzer scale
    response = requests.get(
        url,
        headers=headers,
        params={
            "action": "getmeas",
            "meastypes": "1,5,6,8,11,76,88",
            "category": 1,
            "lastupdate": start_date.strftime("%s"),
        },
        timeout=10,
    )
    withings_results = response.json()["body"]
    wellness = {}
    for measurementdates in withings_results["measuregrps"]:

        # initialize event to push to wellness data
        day = datetime.fromtimestamp(measurementdates["date"]).date()
        if day not in wellness:
            wellness[day] = {}
            wellness[day]["id"] = day.strftime("%Y-%m-%d")
        for measurement in measurementdates["measures"]:
            if measurement["type"] == 1:
                wellness[day]["weight"] = float(
                    measurement["value"] * (10 ** measurement["unit"])
                )
            if measurement["type"] == 6:
                wellness[day]["bodyFat"] = float(
                    measurement["value"] * (10 ** measurement["unit"])
                )
    return wellness


def get_withings_last_measurement(token):
    """Read data from withings"""
    start_date = datetime.today().date() - timedelta(30)  # last 30 days
    # start_date = datetime(2022,1,1)  # override to initially get all values
    url = f"{withings_api}/v2/measure"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        url,
        headers=headers,
        params={
            "action": "getmeas",
            "meastypes": "1,6",
            "category": 1,
            "lastupdate": start_date.strftime("%s"),
        },
        timeout=10,
    )
    withings_results = response.json()["body"]
    last_measurement = withings_results["measuregrps"][
        len(withings_results["measuregrps"]) - 1
    ]
    wellness = {}
    wellness["day"] = {}
    wellness["day"] = datetime.fromtimestamp(last_measurement["modified"]).date()
    for measurement in last_measurement["measures"]:
        if measurement["type"] == 1:
            wellness["weight"] = float(
                measurement["value"] * (10 ** measurement["unit"])
            )
        if measurement["type"] == 6:
            wellness["bodyFat"] = float(
                measurement["value"] * (10 ** measurement["unit"])
            )
    return wellness
