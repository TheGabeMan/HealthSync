"""Send telegram message to a telegram group"""
import os
import sys
from datetime import date

import requests
from dotenv import load_dotenv

load_dotenv()


def get_telegram_creds():
    """Load Telegram API token and channel ID"""
    telegram_api = os.getenv("TELEGRAMAPI")
    telegram_channel_id = os.getenv("TELEGRAMCHANNELID")
    if telegram_api is None or telegram_channel_id is None:
        # main.debuglog("Either telegram api or telegram channel id in .env is null")
        sys.exit()

    return telegram_api, telegram_channel_id


def send_telegram_message(message):
    """Send a message to telegram in a specific group"""
    telegram_api, telegram_channel_id = get_telegram_creds()

    url = (
        f"https://api.telegram.org/bot{telegram_api}/sendMessage?chat_id="
        f"{telegram_channel_id}&text={message}"
    )
    response = requests.post(url=url, timeout=15)
    if response.status_code != 200:
        print("Error while posting to telegram API %s", response.status_code)


def create_body_text(
    user_weight, withings_read_ok, wahoo_send_ok, intervals_send_ok, strava_send_ok, fitbit_send_ok
):
    """Create a body text for the telegram message"""
    today = date.today().strftime("%d-%m-%Y")
    text = "HealthSync info for " + today + "\n"
    if withings_read_ok:
        text += "Weight read from Withings " + str(user_weight)+ "\n"
    else:
        text += "No info read from Withings" + "\n"

    text += "Data sent to Wahoo " + str(wahoo_send_ok) + "\n"
    text += "Data sent to Intervals " + str(intervals_send_ok) + "\n"
    text += "Data sent to Strava " + str(strava_send_ok) + "\n"
    text += "Data sent to Fitbit " + str(fitbit_send_ok) + "\n"
    return text
