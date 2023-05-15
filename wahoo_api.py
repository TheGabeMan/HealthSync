"""
    All Wahoo modules to talk to the Wahoo API
    Infomation at: https://developers.wahooligan.com/cloud
"""

import json
import logging
import os
import sys
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
wahoo_scopes = "user_write+email+workouts_read+workouts_write+power_zones_read\
                +power_zones_write+offline_data+user_read"


def wahoo_authenticate():
    """Setup Authentication with Wahoo API"""
    url = f"{wahoo_api}/oauth/authorize?client_id={wahoo_client_id}\
            &redirect_uri={wahoo_redirect_uri}&response_type=code\
            &scope={wahoo_scopes}"
    print(
        f"No token found, webbrowser will open, authorize the application \
            and copy paste the code section or open URL manually {url}"
    )
    logging.info(
        "No token found, webbrowser will open, authorize the \
        application and copy paste the code section"
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
    res = requests.post(f"{wahoo_api}/oauth/token", params=paramdata, timeout=10)
    out = res.json()
    if res.status_code == 200:
        with open(wahoo_cfg, "w", encoding="utf8") as file:
            json.dump(out, file)
            file.close()
        return out["access_token"]
    if res.status_code != 200:
        print("Wahoo authentication failed:")
        print(out)
        logging.info("Wahoo authentication failed:")
        logging.info(out)
        sys.exit()


def wahoo_refresh(token):
    """refresh current token
    this makes sure we won't have to reauthorize again."""

    url = f"{wahoo_api}/oauth/token"
    res = requests.post(
        url,
        params={
            "client_id": wahoo_client_id,
            "client_secret": wahoo_secret,
            "action": "requesttoken",
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
        },
        timeout=10,
    )
    out = res.json()
    if res.status_code == 200:
        with open(wahoo_cfg, "w", encoding="utf8") as file:
            json.dump(out, file)
            file.close()
        return out["access_token"]
    if res.status_code != 200:
        logging.info("Wahoo token refresh failed")
        logging.info(out)
        sys.exit()


def get_wahoo_user(token):
    """Read user information from Wahoo"""
    url = f"{wahoo_api}/v1/user"
    res = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    return res.json()


def set_wahoo_user_weight(token, weight):
    """Write the weight to the Wahoo user settings"""
    # TODO: Which function should be used? write_weight_wahoo
    #       or set_wahoo_user_weight
    url = f"{wahoo_api}/v1/user"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"user[weight]": f"{weight}"}
    res = requests.put(url, headers=headers, data=data, timeout=10)
    if res.status_code != 200:
        print("There was an error writing to Wahoo API:")
        print(res.json())
        logging.info("There was an error writing to Wahoo API:")
        logging.info(res.json())
    else:
        print(f"Succesful writing weight {weight} to Wahoo API")
        logging.info("Succesful writing weight %s to Wahoo API", weight)


def write_weight_wahoo(user_weight):
    """Write the weight to the Wahoo user settings"""
    # TODO: Which function should be used? write_weight_wahoo
    #       or set_wahoo_user_weight

    wahoo_access_token = (
        wahoo_refresh(json.load(open(wahoo_cfg, encoding="utf8")))
        if os.path.isfile(wahoo_cfg)
        else wahoo_authenticate()
    )
    wahoo_user_info = get_wahoo_user(wahoo_access_token)
    logging.info(
        "Retreived Wahoo userid %s for %s %s",
        wahoo_user_info["id"],
        wahoo_user_info["first"],
        wahoo_user_info["last"],
    )

    set_wahoo_user_weight(wahoo_access_token, user_weight)
