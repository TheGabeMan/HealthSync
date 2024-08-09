"""
    FitBit API
    https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/oauth2-tutorial/
"""

import json
import logging
import os
import sys
from datetime import datetime
import base64
import webbrowser
import secrets
import hashlib
from dotenv import load_dotenv
import requests

load_dotenv()

# Strava API access
fitbit_client_id = os.getenv("fitbit_client_id")
fitbit_client_secret = os.getenv("fitbit_client_secret")
fitbit_token_url = os.getenv("fitbit_token_url")
fitbit_cfg = "fitbit.json"

# Fitbit URLs to use for the API call
dateparam = datetime.now().strftime("%Y-%m-%d")
urlDict = {
    "activities": "https://api.fitbit.com/1/user/-/activities/date/" + dateparam + ".json",
    "weight": "https://api.fitbit.com/1/user/-/body/log/weight/date/" + dateparam + ".json",
    "set_weight": "https://api.fitbit.com/1/user/-/body/log/weight.json",
    "set_bodyfat": "https://api.fitbit.com/1/user/-/body/log/fat.json",
    "water": "https://api.fitbit.com/1/user/-/foods/log/date/" + dateparam + ".json",
    "sleep": "https://api.fitbit.com/1.2/user/-/sleep/date/" + dateparam + ".json",
    "user": "https://api.fitbit.com/1/user/-/profile.json",
    "heartrate": "https://api.fitbit.com/1/user/-/activities/heart/date/" + dateparam + "/1d.json",
}

# # def main():
#     """Main function for testing"""
#     # fitbit_set_weight(user_weight, user_fat)
#     # fitbit_introspect(fitbit_access_token)

def fitbit_read_user():
    """Read user info info from fitbit"""
    fitbit_access_token = (
        fitbit_refresh(json.load(open(fitbit_cfg, encoding="utf8")))
        if os.path.isfile(fitbit_cfg)
        else fitbit_authenticate()
    )

    headers = {
        "Authorization": f"Bearer {fitbit_access_token}",
        "accept": "application/json",
    }

    # urlDict["user"] = https://api.fitbit.com/1/user/-/profile.json
    response = requests.get(urlDict["user"], headers=headers, timeout=10)
    print("User info:", response.json()["user"]["fullName"])
    logging.info("User info")
    logging.info("User weight")

    # urlDict["weight"] = https://api.fitbit.com/1/user/-/body/log/weight/date/
    response = requests.get(urlDict["weight"], headers=headers, timeout=10)
    return fitbit_access_token


def fitbit_set_weight(user_weight,user_fat):
    """Write user weight to fitbit"""
    
    ''' Get tokens '''
    fitbit_access_token = fitbit_read_user()
    today = datetime.now().strftime("%Y-%m-%d")

    ''' Now writing body weight to fitbit '''
    dataweight = {"weight": user_weight, "date": today}
    content_length_weight = len(str(dataweight))

    headers = {
        "Authorization": f"Bearer {fitbit_access_token}",
        "accept": "application/json",
        "content-length": str(content_length_weight),
    }
    response = requests.post(
        urlDict["set_weight"], data=dataweight, headers=headers, timeout=10
    )
    if response.status_code != 201:
            print("There was an error writing to Fitbit API:")
            logging.info("There was an error writing to Fitbit API:")
            logging.info(response.json())
            return False

    print(f"Succesful writing weight {user_weight} to FitBit API")
    logging.info("Succesful writing weight %s to FitBit API", user_weight)

    ''' Now writing body fat to fitbit '''
    datafat = {"fat": user_fat, "date": today}
    content_length_fat = len(str(datafat))

    headers = {
        "Authorization": f"Bearer {fitbit_access_token}",
        "accept": "application/json",
        "content-length": str(content_length_weight),
    }
    response = requests.post(
        urlDict["set_bodyfat"], data=datafat, headers=headers, timeout=10
    )

    if response.status_code != 201:
            print("There was an error writing fat to Fitbit API:")
            logging.info("There was an error writing fat to Fitbit API:")
            logging.info(response.json())
            return False

    print(f"Succesful writing body fat {user_fat} to FitBit API")
    logging.info("Succesful writing weight %s to FitBit API", user_fat)
    return True



def fitbit_introspect(fitbit_access_token):
    """check token permissions for problem solving """
    url = "https://api.fitbit.com/1.1/oauth2/introspect"
    headers = {
        "Authorization": f"Bearer {fitbit_access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = f"token={fitbit_access_token}"
    response = requests.post(url, data=data, headers=headers, timeout=10)
    print(response.json())


def fitbit_refresh(token):
    """Refresh fitbit token"""
    url = "https://api.fitbit.com/oauth2/token"
    encoded_cred = f"{fitbit_client_id}:{fitbit_client_secret}"
    basic_token = base64.b64encode(bytes(encoded_cred, "utf8")).decode("utf-8")

    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    params = {
        "grant_type": "refresh_token",
        "refresh_token": token["refresh_token"],
    }

    response = requests.post(
        url,
        params=params,
        headers=headers,
        timeout=10,
    )
    output = response.json()

    if response.status_code == 200:
        json.dump(output, open(fitbit_cfg, "w", encoding="utf8"))
        return output["access_token"]

    print("Authenication failed")
    logging.info("Authenication failed")
    logging.info(output)
    sys.exit()


def fitbit_authenticate():
    """Get a new Token"""
    code_verifier = secrets.token_urlsafe(96)
    hashed = hashlib.sha256(code_verifier.encode("ascii")).digest()
    encoded = base64.urlsafe_b64encode(hashed)
    code_challenge = encoded.decode("ascii")[:-1]

    encoded_cred = f"{fitbit_client_id}:{fitbit_client_secret}"
    basic_token = base64.b64encode(bytes(encoded_cred, "utf8")).decode("utf-8")
    print(f"Client ID: {fitbit_client_id}")
    url = "https://www.fitbit.com/oauth2/authorize"
    params = {
        "response_type": "code",
        "client_id": fitbit_client_id,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "scope": "activity heartrate profile sleep weight",
    }

    response = requests.get(url, params=params, timeout=10)
    
    webbrowser.open(response.url, new=2)
    print(f"If browser didn't open, copy this link into your browser: {response.url}")
    
    fitbit_code = input(
        "Copy the authorization code located between the code parameter name and the string #_=_     : "
    )

    params = {
        "client_id": fitbit_client_id,
        "code": fitbit_code,
        "code_verifier": code_verifier,
        "grant_type": "authorization_code",
    }
    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(
        fitbit_token_url, params=params, headers=headers, timeout=10
    )
    output = response.json()
    logging.info(response.json())
    if response.status_code == 200:
        json.dump(output, open(fitbit_cfg, "w", encoding="utf8"))
        return output["access_token"]

    print("Authenication failed")
    logging.info(output)
    sys.exit()
