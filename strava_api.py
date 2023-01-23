"""
    All Strava modules to talk to the Strava API
    Infomation at: https://developers.strava.com/
"""

import json
import logging
import os
import webbrowser
from dotenv import load_dotenv

import requests

load_dotenv()

# Strava API access
strava_athlete_id = os.getenv("strava_athlete_id")
strava_client_secret = os.getenv("strava_client_secret")
strava_cfg = "strava.json"
strava_url = "https://www.strava.com/oauth"
strava_api = "https://www.strava.com/api/v3"


def strava_authenticate():
    print(
        "No token found, webbrowser will open, authorize the application and copy paste the code section"
    )
    logging.info("No token found, webbrowser will open, authorize the application and copy paste the code section")
    url = (
        "%s/authorize?client_id=%s&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:write,read"
        % (strava_url, strava_athlete_id)
    )
    webbrowser.open(url, new=2)
    strava_code = input("Insert the code fromthe URL after authorizing: ")
    paramdata = {
        "client_id": strava_athlete_id,
        "client_secret": strava_client_secret,
        "code": strava_code,
        "grant_type": "authorization_code",
    }
    res = requests.post(url="%s/token" % strava_url, data=paramdata)
    out = res.json()
    if res.status_code == 200:
        json.dump(out, open(strava_cfg, "w"))
        return out["access_token"]
    else:
        print("Strava authentication failed:")
        print(out)
        logging.info("Strava authentication failed:")
        logging.info(out)
        exit()


def strava_refresh(token):
    url = "%s/token" % strava_url
    res = requests.post(
        url,
        params={
            "client_id": strava_athlete_id,
            "client_secret": strava_client_secret,
            "action": "requesttoken",
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
        },
    )
    out = res.json()
    if res.status_code == 200:
        json.dump(out, open(strava_cfg, "w"))
        return out["access_token"]
    else:
        print(out)
        exit()


def get_strava_user_info(token):
    url = "%s/athlete" % strava_api
    headers = {"Authorization": "Bearer %s" % token}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("There was an error reading from Strava API:")
        print(res.json())
        logging.info("There was an error reading from Strava API:")
        logging.info(res.json())
    else:
        logging.info('Succesful reading from Strava API')
        return res.json()


def set_strava_weight(user_weight):
    # Write to Strava
    # TODO: make function better, os.path.isfile is probably no longer needed
    #       since we already have a token now
    strava_access_token = (
        strava_refresh(json.load(open(strava_cfg)))
        if os.path.isfile(strava_cfg)
        else strava_authenticate()
    )
    strava_user_info = get_strava_user_info(strava_access_token)
    set_strava_user_weight(
        strava_access_token, float(user_weight), strava_user_info["id"]
    )  # For Strava the user weight must be of type float


def set_strava_user_weight(token, weight, user_id):
    # TODO: check if function is still being used
    url = "%s/athlete" % strava_api
    headers = {"Authorization": "Bearer %s" % token}
    data = {"weight": weight, "id": user_id}
    res = requests.put(url, headers=headers, data=data)
    if res.status_code != 200:
        print("There was an error writing to Strava API:")
        print(res.json())
        logging.info("There was an error writing to Strava API:")
        logging.info(res.json())

    else:
        print("Succesful writing weight to Strava API")
        logging.info("Succesful writing weight to Strava API")
