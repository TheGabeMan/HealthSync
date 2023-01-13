# config section #
##################
import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from dotenv import load_dotenv


## Load .env file
load_dotenv()

## intervals.icu api credentials
icu_athlete_id = os.getenv('icu_athlete_id')
icu_api_key = os.getenv('icu_api_key')
# fixed config - no need to change those
icu_api = 'https://intervals.icu/api/v1/athlete/%s' % icu_athlete_id

## withings_client_id, withings_client_secret and withings_redirect_uri from withings app - register on https://developer.withings.com/dashboard/
withings_client_id = os.getenv('withings_client_id')
withings_client_secret = os.getenv('withings_client_secret')
withings_redirect_uri = os.getenv('withings_redirect_uri')
# fixed config - no need to change those
withings_api = 'https://wbsapi.withings.net/v2'

## ConfigFile for withings token and API info
withings_cfg = 'withings.json'

# fields - set to None to not push them to intervals
# fields must exist as wellness fields (custom or default)
weight_field = 'weight'         # withings weight scales
bodyfat_field = 'bodyFat'       # withings weight scales
diastolic_field = None          # withings blood pressure devices (BPM Core, ...) if needed set field to 'diastolic'
systolic_field = None           # withings blood pressure devices (BPM Core, ...) if needed set field to 'systolic'
temp_field = None               # when you insert manual temperature readings in the withings app, this should do. If needed set field to 'BodyTemperature'

def main():
    # authorize or refresh
    access_token = refresh(json.load(open(withings_cfg))) if os.path.isfile(withings_cfg) else authenticate()

    wellness = {}
    data = get_measurements(access_token)
    for group in data['measuregrps']:

        # initialize event to push to wellness data
        day = datetime.fromtimestamp(group['date']).date()
        if day not in wellness: wellness[day] = {}

        # iterate over measurements
        for m in group['measures']:

            # fields as defined above
            if weight_field and m['type'] == 1: wellness[day][weight_field] = float(m['value'] * (10 ** m['unit']))         # weight in kg
            if bodyfat_field and m['type'] == 6: wellness[day][bodyfat_field] = float(m['value'] * (10 ** m['unit']))       # body fat in %
            if diastolic_field and m['type'] == 9: wellness[day][diastolic_field] = float(m['value'] * (10 ** m['unit']))   # in mmHg
            if systolic_field and m['type'] == 10: wellness[day][systolic_field] = float(m['value'] * (10 ** m['unit']))    # in mmHg
            if temp_field and m['type'] in [71,73]: wellness[day][temp_field] = float(m['value'] * (10 ** m['unit']))       # in celsius
            # the withings temperature thingy normally would be the source for that, but for what it does it's a bit too pricy for me
            # if someone has one or wants me to have one ;) I can look into this further and adjust this script accordingly.
              
    for day, data in sorted(wellness.items()):
        data['id'] = day.strftime('%Y-%m-%d')
        set_wellness(data)

def set_wellness(event):
    requests.packages.urllib3.disable_warnings()
    res = requests.put('%s/wellness/%s' % (icu_api, event['id']), auth=HTTPBasicAuth('API_KEY',icu_api_key), json=event, verify=False)
    if res.status_code != 200:
        print('upload wellness data failed with status code:', res.status_code)
        print(res.json())
    else:
        print('Upload welness data to intervals.icu succesfull')

def authenticate():
    if len(sys.argv) > 1:
        paramdata = {
            'action': 'requesttoken', 
            'code': sys.argv[1],
            'client_id': withings_client_id, 
            'client_secret': withings_client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': withings_redirect_uri,
        }
        print( 'ParamData = ', paramdata)
        res = requests.post('%s/oauth2' % withings_api, params = paramdata )
        out = res.json()
        if out['status'] == 0:
            json.dump(out['body'], open(withings_cfg,'w'))
            return out['body']['access_token']
        else:
            print('authentication failed:')
            print(out)
            exit()
    else:
        print('click the link below, authenticate and start this tool again with the code (you should see that in the url) as parameter')
        print('https://account.withings.com/oauth2_user/authorize2?response_type=code&withings_client_id=%s&state=intervals&scope=user.metrics&withings_redirect_uri=%s' % (withings_client_id, withings_redirect_uri))
        exit()

def refresh(data):
    """refresh current token
    this makes sure we won't have to reauthorize again."""

    url = '%s/oauth2' % withings_api
    res = requests.post(url, params = {
        'client_id': withings_client_id, 'client_secret': withings_client_secret,
        'action': 'requesttoken', 'grant_type': 'refresh_token',
        'refresh_token': data['refresh_token'],
    })
    out = res.json()
    if out['status'] == 0:
        json.dump(out['body'], open(withings_cfg,'w'))
        return out['body']['access_token']
    else:
        print(out)
        exit()

def get_measurements(token):
    start = datetime.today().date() - timedelta(7)          # last 7 days
    #start = datetime(2022,1,1)                             # override to initially get all values
    
    url = '%s/measure' % withings_api
    res = requests.get(url, headers={'Authorization': 'Bearer %s' % token}, params = {
        'action': 'getmeas', 'meastypes': '1,6,9,10,71,73',
        'category': 1, 'lastupdate': start.strftime('%s'),
    })
    return res.json()['body']

if __name__ == '__main__': exit(main())