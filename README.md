<!-- PROJECT SHIELDS -->
[![GitHub Activity][commits-shield]][commits]
[![GitHub Last Commit][last-commit-shield]][commits]
[![Linting][linting-shield]][linting-url]

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE.md)
[![Contributors][contributors-shield]][contributors-url]

[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

# HealthSync
With this Python Script I'm trying to sync my healthdata between severall websites and later on I might add it to my own MySQL DB.

Currently the only working script is:
- healthsync.py: this script should be started as: 'python3 healthsync.py --weight <KG>'
Your weight will then be written to Strava, Intervals.icu and Wahoo.

To make this work, download "healthsync.py" and "env.md". Rename the "env.md" file to ".env", it will become a hidden file.
Now edit the ".env" file with the values you can find on the developer pages of each company:
- intervals.icu -> https://intervals.icu/settings and find "Developer Settings". There you can find your Athlete ID and generate an API key.
- strava.com -> goto settings -> My API application -> generate a new application. The callback domain doesn't matter as long as it works. In my script I'll use localhost. Copy client ID and Client Secret to the ".env" file as "strava_athlete_id" and "strava_client_secret".
- Wahoo -> https://developers.wahooligan.com/ create an account and request an Application. Make sure these callback url is working, but it can be just any website. The request for your application might take 1 or 2 days to process and then you'll have an Application token and a Secret in your developer portal. Copy them into the ".env" file as wahoo_client_id (application token) and wahoo_secret.

After this you can run the script as:
python3 healthsync.py --weight <your weight in KG>
for example:
python3 healthsync.py 81

On first run, you will have a browser window popup for Wahoo and Strava. Both will ask you to authorize the application and will present a new url to a website like this:
https://yourwebsite/?code=mcP85FyCs2pe1wlsF0OxREWknujNRkVge4M3gX8Ljpo
Copy the code part 'mcP85FyCs2pe1wlsF0OxREWknujNRkVge4M3gX8Ljpo' and enter it into the prompt of the script. After this a token will be written into local json files (strava.json and wahoo.json). As long as these files are present, you won't have to do this procedure again. You can however always delete the json files if needed.

# Warning!
Be aware this is a project in the very early stages and therefore very basic. I have a big list of todo's, like better sanity checks and error handling. I also want to add more APIs and more metrics to sync. Just strugling with how to have users all the options.

<a href="https://www.buymeacoffee.com/thegabeman" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

























- (not needed !!! For future use. Withings.com -> https://developer.withings.com/developer-guide/v3/withings-solutions/app-to-app-solution create an account and create an app )
