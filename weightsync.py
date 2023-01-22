""" 13u28
    config section
"""

# from genericpath import isfile
import os
import sys
import json
import requests
import webbrowser
import logging
import getopt
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

logging.basicConfig(filename='weightsync.log', 
                    encoding='utf-8', 
                    level=logging.DEBUG)
'''
    logging.debug('This message should go to the log file')
    logging.info('So should this')
    logging.warning('And this, too')
    logging.error('And non-ASCII stuff, too, like Øresund and Malmö')
'''

"""
    Load .env file and environment settings
"""
load_dotenv()

# intervals.icu API access
icu_athlete_id = os.getenv("icu_athlete_id")
icu_api_key = os.getenv("icu_api_key")
icu_api = "https://intervals.icu/api/v1/athlete/%s" % icu_athlete_id

# Wahoo API access
wahoo_client_id = os.getenv("wahoo_client_id")
wahoo_secret = os.getenv("wahoo_secret")
wahoo_redirect_uri = os.getenv("wahoo_redirect_uri")
wahoo_api = "https://api.wahooligan.com"
wahoo_cfg = "wahoo.json"
wahoo_scopes = "user_write+email+workouts_read+workouts_write+power_zones_read+power_zones_write+offline_data+user_read"

# Strava API access
strava_athlete_id = os.getenv("strava_athlete_id")
strava_client_secret = os.getenv("strava_client_secret")
strava_cfg = "strava.json"
strava_url = "https://www.strava.com/oauth"
strava_api = "https://www.strava.com/api/v3"

# Withings API access
withings_client_id = os.getenv("withings_client_id")
withings_client_secret = os.getenv("withings_client_secret")
withings_cfg = "withings.json"
withings_redirect_uri = os.getenv("withings_redirect_uri")
withings_api = "https://wbsapi.withings.net/v2"


"""
    Start of main script
"""


def main():

    arg_options = check_arguments(sys.argv)

    if "manual" in arg_options:
        print("Manual weight entry")

    sys.exit()


    if len(sys.argv) > 1 and sys.sys.argv[1] != 'withings':
        logging.info('Found weight as input.')
        user_weight = sys.argv[1]    
        # Todo: Check for correct weight value

        # Write the weight to Wahoo
        write_weight_wahoo(user_weight)

        # Write the weight to intervals.icu
        write_weight_intervals(user_weight)

        # Write the weight to Strava
        write_weight_strave(user_weight)

    elif len(sys.argv) > 1 and sys.sys.argv[1] == 'withings':
        withings_access_token = (
            withings_refresh(json.load(open(withings_cfg)))
            if os.path.isfile(withings_cfg)
            else withings_authenticate()
        )

        # Read from intervals.icu the last 30 days of wellness data
        icu_wellness_data = get_icu_wellness()
        print(' ************ ICU WELLNESS DATA ***********')
        print('\r\n')
        print('')
        print(icu_wellness_data)

        print(' ************ ICU FILTER DATA ***********')
        print('\r\n')
        print('')
        output_dict = [x for x in icu_wellness_data if x['weight'] is not None]
        print(output_dict)

        # Todo: Read intervals to find last data for which there was a known
        # weight measurement. Based on last intervals.icu measurment data
        # get withings data
        # For now we just go back 7 days
        withings_measurements = get_withings_measurements(withings_access_token)
        print('***********    WITHINGS    DATA ***********')
        print("Withings data:\n\r",withings_measurements)
        exit()
    else:
        print('usage not correct. Script should be called with your weight in KG or using the option "withings" to read the weight from withings.' )


def check_arguments(arguments):
    # todo: Switch to ArgParse ( https://realpython.com/command-line-interfaces-python-argparse/ )
    try:
        opts, args = getopt.getopt(arguments[1:],
                                   "",
                                   ["debug", "weight=", "withings"]
                                   )
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for opt in opts:
        if opt == "--weight":
            print("Weight from cmdline: %s" % opt[1])
            if not isfloat(arg):
                print("Received weight is not a floating-point number.")
                usage()
                sys.exit()
        else:
            assert False, "unhandled option"
            usage()


def isfloat(num):
    # Check if num is a floating-point
    try:
        float(num)
        return True
    except ValueError:
        return False


def usage():
        print('Run script as: weightsync.py --help --weight <weight in kg> --withings')
        print('--weight <kg>    manual weight input in KG, will be synced to other applications')
        print('--withings   sync data from withings to other applications')
        print('--verbose    verbose logging on')


def write_weight_wahoo( user_weight):

    # Get Wahoo_access_token or refresh the token
    wahoo_access_token = (
        wahoo_refresh(json.load(open(wahoo_cfg)))
        if os.path.isfile(wahoo_cfg)
        else wahoo_authenticate()
    )
    wahoo_user_info = get_wahoo_user(wahoo_access_token)
    print(
        "Retreived Wahoo userid %s for %s %s"
        % (wahoo_user_info["id"], wahoo_user_info["first"], 
            wahoo_user_info["last"]
           )
          )

    set_wahoo_user_weight(wahoo_access_token, user_weight)


def write_weight_intervals( user_weight):
    # Write to Intervals.icu
    datetoday = (datetime.today().date()).strftime("%Y-%m-%d")  # format needed: '2023-01-22'
    icu_data = json.loads('{ "weight": %s, "id": %s}' %
                          (user_weight, datetoday))
    set_icu_wellness(icu_data)


def write_weight_strave( user_weight):
    # Write to Strava
    strava_access_token = (
        strava_refresh(json.load(open(strava_cfg)))
        if os.path.isfile(strava_cfg)
        else strava_authenticate()
    )
    strava_user_info = get_strava_user_info(strava_access_token)
    set_strava_user_weight(
        strava_access_token, float(user_weight), strava_user_info["id"]
    )  # For Strava the user weight must be of type float

    print("Exit main")

def get_wahoo_user(token):
    url = "%s/v1/user" % wahoo_api
    res = requests.get(url, headers={"Authorization": "Bearer %s" % token})
    return res.json()


def set_wahoo_user_weight(token, weight):
    url = "%s/v1/user" % wahoo_api
    headers = {"Authorization": "Bearer %s" % token}
    data = {"user[weight]": "%s" % weight}
    res = requests.put(url, headers=headers, data=data)
    if res.status_code != 200:
        print("There was an error writing to Wahoo API:")
        print(res.json())
    else:
        print("Succesful writing weight to Wahoo API")


def wahoo_authenticate():
    print(
        "No token found, webbrowser will open, authorize the application and copy paste the code section"
    )
    url = (
        "%s/oauth/authorize?client_id=%s&redirect_uri=%s&response_type=code&scope=%s"
        % (wahoo_api, wahoo_client_id, wahoo_redirect_uri, wahoo_scopes)
    )
    webbrowser.open(url, new=2)
    wahoo_code = input("Insert the code fromthe URL after authorizing: ")
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
        print("authentication failed:")
        print(out)
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
        print(out)
        exit()


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
    this makes sure we won't have to reauthorize again."""

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
    # start = datetime(2022,1,1)                             # override to initially get all values
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
            wellness[day]['id'] = day.strftime("%Y-%m-%d")
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


def set_icu_wellness(data):
    requests.packages.urllib3.disable_warnings()
    '''
    res = requests.put(
        "%s/wellness/%s" % (icu_api, data["id"]),
        auth=HTTPBasicAuth("API_KEY", icu_api_key),
        json=data,
        verify=False,
    )
    if res.status_code != 200:
        print("upload to intervals.icu failed with status code:", res.status_code)
        print(res.json())
    else:
        print("Succesful writing weight to intervals.icu")
    '''


def get_icu_wellness():
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
        print("Get info fromintervals.icu failed with status code:", res.status_code)
        print(res.json())
    return res.json()


def strava_authenticate():
    print(
        "No token found, webbrowser will open, authorize the application and copy paste the code section"
    )
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
        print("authentication failed:")
        print(out)
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
    else:
        print("Succesful reading from Strava API")
        return res.json()


def set_strava_user_weight(token, weight, user_id):
    url = "%s/athlete" % strava_api
    headers = {"Authorization": "Bearer %s" % token}
    data = {"weight": weight, "id": user_id}
    res = requests.put(url, headers=headers, data=data)
    if res.status_code != 200:
        print("There was an error writing to Strava API:")
        print(res.json())
    else:
        print("Succesful writing weight to Strava API")


if __name__ == "__main__":
    exit(main())
