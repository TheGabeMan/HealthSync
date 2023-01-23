"""
    All withings modules to talk to the Withings API
    Infomation at: https://developer.withings.com/
"""


from datetime import datetime, timedelta
import json
import webbrowser
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Withings API access
withings_client_id = os.getenv("withings_client_id")
withings_client_secret = os.getenv("withings_client_secret")
withings_cfg = "withings.json"
withings_redirect_uri = os.getenv("withings_redirect_uri")
withings_api = "https://wbsapi.withings.net/v2"


def withings_authenticate():
    print(
        "No token found, webbrowser will open, authorize the application and copy past the code section"
    )
    url = (
        "https://account.withings.com/oauth2/authorize?response_type=code&withings_client_id=%s&state=interval&scope=user.metrics&withings_redirect_uri=%s"
        % (withings_client_id, withings_redirect_uri)
    )

    webbrowser.open(url, new=2)
    withings_code = input("Insert the code fromthe URL after authorizing: ")
    paramdata = {
        "action": "requesttoken",
        "code": withings_code,
        "client_id": withings_client_id,
        "client_secret": withings_client_secret,
        "grant_type": "authorization_code",
        "redirect_uri": withings_redirect_uri,
    }
    res = requests.post("%s/oauth2" % withings_api, params=paramdata)
    out = res.json()
    if res.status == 200:
        json.dump(out["body"], open(withings_cfg, "w"))
        return out["body"]["access_token"]
    else:
        print("authentication failed:")
        print(out)
        exit()


def withings_refresh(token):
    """refresh current token
    this makes sure we won't have to reauthorize again.
    """

    url = "%s/oauth2" % withings_api
    res = requests.post(
        url,
        params={
            "client_id": withings_client_id,
            "client_secret": withings_client_secret,
            "action": "requesttoken",
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
        },
    )
    out = res.json()
    if out["status"] == 0:
        json.dump(out["body"], open(withings_cfg, "w"))
        return out["body"]["access_token"]
    else:
        print(out)
        exit()


def get_withings_measurements(token):
    start = datetime.today().date() - timedelta(7)  # last 7 days
    # start = datetime(2022,1,1)  # override to initially get all values
    url = "%s/measure" % withings_api
    res = requests.get(
        url,
        headers={"Authorization": "Bearer %s" % token},
        params={
            "action": "getmeas",
            "meastypes": "1,6",
            "category": 1,
            "lastupdate": start.strftime("%s"),
        },
    )
    withings_results = res.json()["body"]
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
