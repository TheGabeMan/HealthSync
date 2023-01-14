
Much of this script is based on: https://gist.github.com/fruitloop/7e79eeab9fd4ba7d2be5cdf8175d2267
By: https://gist.github.com/fruitloop

# HealthSync
With this Python Script I'm trying to sync my healthdata between severall websites and later on I might add it to my own MySQL DB.

Currently here are three very bare bones scripts:
- weightsync.py: this script asks the user for his/her weight and writes the weight to intervals.icu and Wahoo
- main.py: reading info from intervals.icu
- withings.py: this will read data from Withings and write wellness data to intervals.icu
- wahoo.py: this will read user info from Wahoo and as first test it writes the weight back to wahoo

To make this work, rename the "env.md" file to ".env"
In the file edit the values as you can find them on the developer pages of each company:
- intervals.icu -> https://intervals.icu/settings and find "Developer Settings". There you can find your Athlete ID and generate an API key.
- Withings.com -> https://developer.withings.com/developer-guide/v3/withings-solutions/app-to-app-solution create an account and create an app
- Wahoo -> https://developers.wahooligan.com/ create an account and request an Application
