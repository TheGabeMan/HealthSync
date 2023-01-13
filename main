import os
import requests
import datetime
from dotenv import load_dotenv

def get_athlete_info(intervals_api_key, base_url, athlete_id):
    url = "{}/api/v1/athlete/{}".format(base_url, athlete_id)
    print( "Athlete info requested: ", url)
    response_data = get_api_data( "GET", url, intervals_api_key)
    return response_data

def get_athlete_welness(intervals_api_key, base_url, athlete_id, wellness_startdate, wellness_enddate):
    url = "{}/api/v1/athlete/{}/wellness{{ext}}?oldest={}&newest={}".format( base_url,athlete_id, wellness_startdate, wellness_enddate)
    print( "Wellness info requested: ", url)
    response_data = get_api_data( "GET", url, intervals_api_key)
    return response_data

def get_athlete_activities(intervals_api_key, base_url, athlete_id, activities_startdate, activities_enddate):
    url = "{}/api/v1/athlete/{}/activities?oldest={}&newest={}".format( base_url,athlete_id, activities_startdate, activities_enddate)
    print( "Activities requested: ", url)
    response_data = get_api_data( "GET", url, intervals_api_key)
    return response_data

def get_api_data(method, url, intervals_api_key ):
    if method == "GET":
        response = requests.get(url, auth=('API_KEY', intervals_api_key))
        if response.status_code == 401:
            print( "Unauthorized, error code", response.status_code)
        if response.status_code == 403:
            print( "Error accessing resource, error code", response.status_code)
        if response.status_code == 404:
            print( "Resource not found, error code", response.status_code)
        if response.status_code == 422:
            print( "Could not proces object, error code", response.status_code)
    return response


"""
    Main script start
    Default vars
"""

## Load Environment variabelen from .env file
load_dotenv()
athlete_id = os.getenv('athlete_id')
intervals_api_key = os.getenv('intervals_api_key')
base_url = 'https://intervals.icu'
date_today = datetime.date.today()

"""
    Retreive athlete info
"""
athlete_info = get_athlete_info( 
    intervals_api_key=intervals_api_key,
    base_url=base_url,
    athlete_id=athlete_id
).json()

"""
    Basic Athlete infomation like Name, current zones
"""
print( "Information found for Athlete:", athlete_info["name"])
print( "**** icu information ****")
print( "Athlete ID: ", athlete_info["id"])
print( "Resting heart rate:",  athlete_info["icu_resting_hr"])
print( "Weight (kg):",  athlete_info["icu_weight"])
print( "SportSettings: ", len(athlete_info["sportSettings"]))

if len(athlete_info["sportSettings"]) == 0:
    print( "No SportSettings found")
else:
    for sport_setting in athlete_info["sportSettings"]:
        print( sport_setting["id"],sport_setting["ftp"],sport_setting["created"],sport_setting["updated"],sport_setting["max_hr"])


"""
    Retreive athlete wellness info
"""
wellness_info = get_athlete_welness( 
    intervals_api_key=intervals_api_key,
    base_url=base_url,
    athlete_id=athlete_id,
    wellness_startdate="2023-01-01",
    wellness_enddate=date_today
).json()

if len( wellness_info ) == 0:
    print("Geen wellness info gevonden")
else:
   for wellness_data in wellness_info:
    print(wellness_data["id"],wellness_data["updated"],wellness_data["ctl"],wellness_data["atl"],wellness_data["restingHR"],wellness_data["sportInfo"])


"""
    Retreive athlete activities
"""
activities_info = get_athlete_activities( 
    intervals_api_key=intervals_api_key,
    base_url=base_url,
    athlete_id=athlete_id,
    activities_startdate="2023-01-01",
    activities_enddate=date_today
).json()

if len( activities_info) == 0:
    print("Geen activities gevonden")
else:
    for activity in activities_info:
        print(activity["id"],activity["start_date_local"],activity["type"],activity["distance"],activity["total_elevation_gain"],activity["name"])

"""
    Ophalen van data uit intervals:
        - op basis van athlete ID, in MariaDB kijken welke data al aanwezig is
            - zoek laatst bijgewerkte athlete info
            - zoek laatste wellness data
            - zoek laatste activity
        - 

"""
