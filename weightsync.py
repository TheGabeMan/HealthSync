######################################################
# config section 
######################################################
import os
import sys
import json
import requests
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

######################################################
## Start of Main Script
######################################################
def main():

    user_weight = input("What is your current weight? ")
    
    ## Get Wahoo_access_token or refresh the token
    wahoo_access_token = wahoo_refresh(json.load(open(wahoo_cfg))) if os.path.isfile(wahoo_cfg) else wahoo_authenticate()
    wahoo_user_info = get_wahoo_user( wahoo_access_token)
    print( wahoo_user_info['id'] )
    print( 'Retreived userid %s for %s %s' % (wahoo_user_info['id'], wahoo_user_info['first'], wahoo_user_info['last']))
    set_wahoo_user_weight( wahoo_access_token, user_weight)

    ## Write to Intervals.icu
    ## Create JSON for weight today
    icu_data =  json.loads('{ "weight": %s, "id":"2023-01-14"}' % (user_weight))
    set_icu_wellness(icu_data)


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
    if len(sys.argv) > 1:
        paramdata = {
            'action': 'requesttoken', 
            'code': sys.argv[1],
            'client_id': wahoo_client_id,
            'client_secret': wahoo_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': wahoo_redirect_uri
        }
        print( 'ParamData = ', paramdata)
        res = requests.post('%s/oauth/token' % wahoo_api, params = paramdata )
        print( '1 ****** ontvangen resultaat ******', res.json() )
        out = res.json()
        if res.status_code == 200:
            json.dump(out, open(wahoo_cfg,'w'))
            return out['access_token']
        else:
            print('authentication failed:')
            print(out)
            exit()
    else:
        print('click the link below, authenticate and start this tool again with the code (you should see that in the url) as parameter')
        print('%s/oauth/authorize?client_id=%s&redirect_uri=%s&response_type=code&scope=%s' % ( wahoo_api, wahoo_client_id,wahoo_redirect_uri,wahoo_scopes))
        ## print('https://account.withings.com/oauth2_user/authorize2?response_type=code&withings_client_id=%s&state=intervals&scope=user.metrics&withings_redirect_uri=%s' % (withings_client_id, withings_redirect_uri))
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

if __name__ == '__main__': exit(main())
