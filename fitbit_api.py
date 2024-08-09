"""
    FitBit API
    https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/oauth2-tutorial/
"""

# from genericpath import isfile
import json
import logging
import os
import sys

# import datetime
from datetime import datetime
import base64
import webbrowser
import secrets
import hashlib
from dotenv import load_dotenv
import requests

# from requests.exceptions import Timeout

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
    "water": "https://api.fitbit.com/1/user/-/foods/log/date/" + dateparam + ".json",
    "sleep": "https://api.fitbit.com/1.2/user/-/sleep/date/" + dateparam + ".json",
    "user": "https://api.fitbit.com/1/user/-/profile.json",
    "heartrate": "https://api.fitbit.com/1/user/-/activities/heart/date/" + dateparam + "/1d.json",
}


def main():
    """Main function for testing"""
    fitbit_access_token = fitbit_read_user()
    fitbit_set_weight(82, fitbit_access_token)
    fitbit_introspect(fitbit_access_token)


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
    print("User info:", response.json()["user"]["weight"])

    # urlDict["weight"] = https://api.fitbit.com/1/user/-/body/log/weight/date/
    response = requests.get(urlDict["weight"], headers=headers, timeout=10)
    print("Weight URL:", response.json()["weight"])
    return fitbit_access_token


def fitbit_set_weight(weight, fitbit_access_token):
    """Write user weight to fitbit"""
    today = datetime.now().strftime("%Y-%m-%d")
    data = {"weight": weight, "date": today}
    content_length = len(str(data))
    headers = {
        "Authorization": f"Bearer {fitbit_access_token}",
        "accept": "application/json",
        "content-length": str(content_length),
    }
    response = requests.post(
        urlDict["set_weight"], data=data, headers=headers, timeout=10
    )
    print(response.json())


def fitbit_introspect(fitbit_access_token):
    """check token permissions"""
    url = "https://api.fitbit.com/1.1/oauth2/introspect"
    headers = {
        "Authorization": f"Bearer {fitbit_access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = f"token={fitbit_access_token}"
    print(data)

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
    print(output)
    sys.exit()


def fitbit_authenticate():
    """Get a new Token"""
    code_verifier = secrets.token_urlsafe(96)
    hashed = hashlib.sha256(code_verifier.encode("ascii")).digest()
    encoded = base64.urlsafe_b64encode(hashed)
    code_challenge = encoded.decode("ascii")[:-1]

    encoded_cred = f"{fitbit_client_id}:{fitbit_client_secret}"
    basic_token = base64.b64encode(bytes(encoded_cred, "utf8")).decode("utf-8")

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
    fitbit_code = input(
        "Copy the authorization code located between the code parameter name and the string #_=_"
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
    if response.status_code == 200:
        json.dump(output, open(fitbit_cfg, "w", encoding="utf8"))
        return output["access_token"]

    print("Authenication failed")
    print(output)
    sys.exit()


if __name__ == "__main__":
    sys.exit(main())
