"""
    All Wahoo modules to talk to the Wahoo API
    Infomation at: https://developers.wahooligan.com/cloud
"""

import json
import logging
import os
import webbrowser
import requests
from dotenv import load_dotenv

load_dotenv()

# Wahoo API access
wahoo_client_id = os.getenv("wahoo_client_id")
wahoo_secret = os.getenv("wahoo_secret")
wahoo_redirect_uri = os.getenv("wahoo_redirect_uri")
wahoo_api = "https://api.wahooligan.com"
wahoo_cfg = "wahoo.json"
wahoo_scopes = "user_write+email+workouts_read+workouts_write+power_zones_read+power_zones_write+offline_data+user_read"


def wahoo_authenticate():
    print(
        "No token found, webbrowser will open, authorize the application and copy paste the code section"
    )
    logging.info("No token found, webbrowser will open, authorize the application and copy paste the code section")
    url = (
        "%s/oauth/authorize?client_id=%s&redirect_uri=%s&response_type=code&scope=%s"
        % (wahoo_api, wahoo_client_id, wahoo_redirect_uri, wahoo_scopes)
    )
    webbrowser.open(url, new=2)
    wahoo_code = input("Insert the code from the URL after authorizing: ")
    paramdata = {
        "action": "requesttoken",
        "code": wahoo_code,
        "client_id": wahoo_client_id,
        "client_secret": wahoo_secret,
        "grant_type": "authorization_code",
        "redirect_uri": wahoo_redirect_uri,
    }
    res = requests.post("%s/oauth/token" % wahoo_api, params=paramdata)
    out = res.json()
    if res.status_code == 200:
        json.dump(out, open(wahoo_cfg, "w"))
        return out["access_token"]
    else:
        print("Wahoo authentication failed:")
        print(out)
        logging.info("Wahoo authentication failed:")
        logging.info(out)
        exit()


def wahoo_refresh(token):
    """refresh current token
    this makes sure we won't have to reauthorize again."""

    url = "%s/oauth/token" % wahoo_api
    res = requests.post(
        url,
        params={
            "client_id": wahoo_client_id,
            "client_secret": wahoo_secret,
            "action": "requesttoken",
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
        },
    )
    out = res.json()
    if res.status_code == 200:
        json.dump(out, open(wahoo_cfg, "w"))
        return out["access_token"]
    else:
        logging.info("Wahoo token refresh failed")
        logging.info(out)
        exit()


def get_wahoo_user(token):
    url = "%s/v1/user" % wahoo_api
    res = requests.get(url, headers={"Authorization": "Bearer %s" % token})
    return res.json()


def set_wahoo_user_weight(token, weight):
    # TODO: Which function should be used? write_weight_wahoo
    #       or set_wahoo_user_weight
    url = "%s/v1/user" % wahoo_api
    headers = {"Authorization": "Bearer %s" % token}
    data = {"user[weight]": "%s" % weight}
    res = requests.put(url, headers=headers, data=data)
    if res.status_code != 200:
        print("There was an error writing to Wahoo API:")
        print(res.json())
        logging.info("There was an error writing to Wahoo API:")
        logging.info(res.json())
    else:
        print("Succesful writing weight to Wahoo API")
        logging.info("Succesful writing weight to Wahoo API")


def write_weight_wahoo( user_weight):
    # TODO: Which function should be used? write_weight_wahoo
    #       or set_wahoo_user_weight
    # Get Wahoo_access_token or refresh the token
    wahoo_access_token = (
        wahoo_refresh(json.load(open(wahoo_cfg)))
        if os.path.isfile(wahoo_cfg)
        else wahoo_authenticate()
    )
    wahoo_user_info = get_wahoo_user(wahoo_access_token)
    logging.info(
        "Retreived Wahoo userid %s for %s %s"
        % (wahoo_user_info["id"], wahoo_user_info["first"], 
            wahoo_user_info["last"]
           )
          )

    set_wahoo_user_weight(wahoo_access_token, user_weight)
