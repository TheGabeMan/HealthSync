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
    ''' Get Authentication token from Strava '''
    print(
        "No token found, webbrowser will open, authorize the application and \
            copy paste the code section"
    )
    logging.info("No token found, webbrowser will open, authorize the \
        application and copy paste the code section")
    url = (
        f"{strava_url}/authorize?client_id={strava_athlete_id}\
            &response_type=code\
            &redirect_uri=http://localhost/exchange_token\
            &approval_prompt=force\
            &scope=profile:write,read"
        )
    webbrowser.open(url, new=2)
    strava_code = input("Insert the code fromthe URL after authorizing: ")
    paramdata = {
        "client_id": strava_athlete_id,
        "client_secret": strava_client_secret,
        "code": strava_code,
        "grant_type": "authorization_code",
    }
    res = requests.post(url=f"{strava_url}/token",
                        data=paramdata,
                        timeout=10)
    out = res.json()
    if res.status_code == 200:
        json.dump(out,
                  open(strava_cfg,
                       "w",
                       encoding="utf8")
                  )
        return out["access_token"]
    else:
        print("Strava authentication failed:")
        print(out)
        logging.info("Strava authentication failed:")
        logging.info(out)
        exit()


def strava_refresh(token):
    ''' Refresh the Strava token '''
    url = f"{strava_url}/token"
    res = requests.post(
        url,
        params={
            "client_id": strava_athlete_id,
            "client_secret": strava_client_secret,
            "action": "requesttoken",
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
        },
        timeout=10
    )
    out = res.json()
    if res.status_code == 200:
        json.dump(out, open(
                            strava_cfg,
                            "w",
                            encoding="utf8"
                            ))
        return out["access_token"]
    else:
        print(out)
        exit()


def get_strava_user_info(token):
    ''' Read User info from Strava '''
    url = f"{strava_api}/athlete"
    # headers = {f'"Authorization": "Bearer {token}"'}
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
                       url,
                       headers=headers,
                       timeout=10
                       )
    if response.status_code != 200:
        print("There was an error reading from Strava API:")
        print(response.json())
        logging.info("There was an error reading from Strava API:")
        logging.info(response.json())
    else:
        logging.info('Succesful reading from Strava API')
        return response.json()


def set_strava_weight(user_weight):
    ''' Write Weight to Strava '''
    # TODO: make function better, os.path.isfile is probably no longer needed
    #       since we already have a token now
    strava_access_token = (
        strava_refresh(json.load(open(strava_cfg, encoding="utf8")))
        if os.path.isfile(strava_cfg)
        else strava_authenticate()
    )
    strava_user_info = get_strava_user_info(strava_access_token)
    set_strava_user_weight(
        strava_access_token, float(user_weight), strava_user_info["id"]
    )  # For Strava the user weight must be of type float


def set_strava_user_weight(token, weight, user_id):
    ''' Write weight to Strava '''
    # TODO: check if function is still being used
    url = f"{strava_api}/athlete"
    # headers = {f'"Authorization": "Bearer {token}"'}
    headers = {"Authorization": f"Bearer {token}"}
    data = {"weight": weight, "id": user_id}
    res = requests.put(url, headers=headers, data=data, timeout=10)
    if res.status_code != 200:
        print("There was an error writing to Strava API:")
        print(res.json())
        logging.info("There was an error writing to Strava API:")
        logging.info(res.json())

    else:
        print(f"Succesful writing weight {weight} to Strava API")
        logging.info("Succesful writing weight %s to Strava API", weight)
