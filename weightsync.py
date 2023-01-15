######################################################
# config section 
######################################################
import os
import sys
import json
import requests
import webbrowser
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from dotenv import load_dotenv

######################################################
## Load .env file and environment settings
######################################################
load_dotenv()

## intervals.icu api credentials
icu_athlete_id = os.getenv('icu_athlete_id')
icu_api_key = os.getenv('icu_api_key')
icu_api = 'https://intervals.icu/api/v1/athlete/%s' % icu_athlete_id

## Wahoo API access
wahoo_client_id = os.getenv('wahoo_client_id')
wahoo_secret = os.getenv('wahoo_secret')
wahoo_redirect_uri = os.getenv('wahoo_redirect_uri')
wahoo_api = 'https://api.wahooligan.com'
wahoo_cfg = 'wahoo.json'
wahoo_scopes = 'user_write+email+workouts_read+workouts_write+power_zones_read+power_zones_write+offline_data+user_read'

## Strava api credentials
strava_athlete_id = os.getenv('strava_athlete_id')
strava_client_secret = os.getenv('strava_client_secret')
strava_cfg = 'strava.json'
strava_url = 'https://www.strava.com/oauth'
strava_api = 'https://www.strava.com/api/v3'

######################################################
## Start of Main Script
######################################################
def main():

    if len(sys.argv) > 1:
        user_weight = sys.argv[1]
    else:
        user_weight = input("What is your current weight? ")

    ## Get Wahoo_access_token or refresh the token
    wahoo_access_token = wahoo_refresh(json.load(open(wahoo_cfg))) if os.path.isfile(wahoo_cfg) else wahoo_authenticate()
    wahoo_user_info = get_wahoo_user( wahoo_access_token)
    print( 'Retreived Wahoo userid %s for %s %s' % (wahoo_user_info['id'], wahoo_user_info['first'], wahoo_user_info['last']))
    set_wahoo_user_weight( wahoo_access_token, user_weight)

    ## Write to Intervals.icu
    ## Create JSON for weight today
    icu_data =  json.loads('{ "weight": %s, "id":"2023-01-14"}' % (user_weight))
    set_icu_wellness(icu_data)

    ## Write to Strava
    strava_access_token = strava_refresh(json.load(open(strava_cfg))) if os.path.isfile(strava_cfg) else strava_authenticate()
    strava_user_info = get_strava_user_info( strava_access_token)
    set_strava_user_weight( strava_access_token, float(user_weight), strava_user_info['id']  )   ## For Strava the user weight must be of type float

def get_wahoo_user( token ):
    url = '%s/v1/user' % wahoo_api
    res = requests.get(url, headers={'Authorization': 'Bearer %s' % token})
    return res.json() 

def set_wahoo_user_weight( token, weight):
    url = '%s/v1/user' % wahoo_api
    headers = {'Authorization': 'Bearer %s' % token}
    data = {'user[weight]':'%s' % weight}
    res = requests.put( url, headers=headers, data=data)
    if res.status_code != 200:
        print("There was an error writing to Wahoo API:")
        print( res.json())
    else:
        print("Succesful writing weight to Wahoo API")

def wahoo_authenticate():
    '''
    if len(sys.argv) > 1:
        paramdata = {
            'action': 'requesttoken', 
            'code': sys.argv[1],
            'client_id': wahoo_client_id,
            'client_secret': wahoo_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': wahoo_redirect_uri
        }
        res = requests.post('%s/oauth/token' % wahoo_api, params = paramdata )
        out = res.json()
        if res.status_code == 200:
            json.dump(out, open(wahoo_cfg,'w'))
            return out['access_token']
        else:
            print('authentication failed:')
            print(out)
            exit()
    else:
    '''
    print('No token found, webbrowser will open, authorize the application and copy paste the code section')
    url = '%s/oauth/authorize?client_id=%s&redirect_uri=%s&response_type=code&scope=%s' % ( wahoo_api, wahoo_client_id,wahoo_redirect_uri,wahoo_scopes)
    webbrowser.open(url,new=2)
    wahoo_code = input('Insert the code fromthe URL after authorizing: ')
    paramdata = {
        'action': 'requesttoken', 
        'code': wahoo_code,
        'client_id': wahoo_client_id,
        'client_secret': wahoo_secret,
        'grant_type': 'authorization_code',
        'redirect_uri': wahoo_redirect_uri
    }
    res = requests.post('%s/oauth/token' % wahoo_api, params = paramdata )
    out = res.json()
    if res.status_code == 200:
        json.dump(out, open(wahoo_cfg,'w'))
        return out['access_token']
    else:
        print('authentication failed:')
        print(out)
        exit()

def wahoo_refresh(data):
    """refresh current token
    this makes sure we won't have to reauthorize again."""

    url = '%s/oauth/token' % wahoo_api
    res = requests.post(url, params = {
        'client_id': wahoo_client_id, 'client_secret': wahoo_secret,
        'action': 'requesttoken', 'grant_type': 'refresh_token',
        'refresh_token': data['refresh_token'],
    })
    out = res.json()
    if res.status_code == 200:
        json.dump(out, open(wahoo_cfg,'w'))
        return out['access_token']
    else:
        print(out)
        exit()

def set_icu_wellness(event):
    requests.packages.urllib3.disable_warnings()
    res = requests.put('%s/wellness/%s' % (icu_api, event['id']), auth=HTTPBasicAuth('API_KEY',icu_api_key), json=event, verify=False)
    if res.status_code != 200:
        print('upload to intervals.icu failed with status code:', res.status_code)
        print(res.json())
    else:
        print('Succesful writing weight to intervals.icu')

def strava_authenticate():
    '''if len(sys.argv) > 1:
        paramdata = {
            'client_id': strava_athlete_id,
            'client_secret': strava_client_secret,
            'code': sys.argv[1],
            'grant_type': 'authorization_code'
        }
        res = requests.post( url = '%s/token' % strava_url, data = paramdata)
        out = res.json()
        if res.status_code == 200:
            json.dump(out, open(strava_cfg,'w'))
            return out['access_token']
        else:
            print('authentication failed:')
            print(out)
            exit()
    else:'''
    print("No token found, webbrowser will open, authorize the application and copy paste the code section")
    url ='%s/authorize?client_id=%s&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:write,read' % ( strava_url, strava_athlete_id)
    webbrowser.open(url,new=2)
    strava_code = input("Insert the code fromthe URL after authorizing: ")
    paramdata = {
        'client_id': strava_athlete_id,
        'client_secret': strava_client_secret,
        'code': strava_code,
        'grant_type': 'authorization_code'
    }
    res = requests.post( url = '%s/token' % strava_url, data = paramdata)
    out = res.json()
    if res.status_code == 200:
        json.dump(out, open(strava_cfg,'w'))
        return out['access_token']
    else:
        print('authentication failed:')
        print(out)
        exit()

def strava_refresh(data):
    url = '%s/token' % strava_url
    res = requests.post(url, params = {
        'client_id': strava_athlete_id, 
        'client_secret': strava_client_secret,
        'action': 'requesttoken', 
        'grant_type': 'refresh_token',
        'refresh_token': data['refresh_token'],
    })
    out = res.json()
    if res.status_code == 200:
        json.dump(out, open(strava_cfg,'w'))
        return out['access_token']
    else:
        print(out)
        exit()

def get_strava_user_info( token):
    url = '%s/athlete' % strava_api
    headers = {'Authorization': 'Bearer %s' % token}
    res = requests.get( url, headers=headers)
    if res.status_code != 200:
        print("There was an error reading from Strava API:")
        print( res.json())
    else:
        print("Succesful reading from Strava API")
        return res.json()

def set_strava_user_weight( token, weight, user_id):
    url = '%s/athlete' % strava_api
    headers = {'Authorization': 'Bearer %s' % token}
    data = { 'weight': weight, 'id':user_id}
    ## data = {'user[weight]':'%s' % weight}
    res = requests.put( url, headers=headers, data=data)
    if res.status_code != 200:
        print("There was an error writing to Strava API:")
        print( res.json())
    else:
        print("Succesful writing weight to Strava API")


if __name__ == '__main__': exit(main())
