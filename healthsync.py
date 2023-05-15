"""
    config section
"""

# from genericpath import isfile
import sys
import argparse
import logging
import wahoo_api
import strava_api
import intervals_api
import withings_api

logging.basicConfig(filename="weightsync.log",
                    encoding="utf-8",
                    level=logging.INFO)


def main():
    ''' The Main Script'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "apis", nargs="*", help="Use withings, strava API to read weight"
    )
    parser.add_argument(
        "-w",
        "--weight",
        required=False,
        type=float,
        action="store",
        help="Input weight in KG (floating point value)",
    )
    args = parser.parse_args()

    # TODO: Lusje maken om door de args.apis heen te lopen
    if "debug" in args.apis:
        set_logging_debug()

    if args.weight is None:
        logging.info("No weight on commandline, try to retrieve from withings.")
        user_weight = withings_api.get_withings_user_weight()

    else:
        logging.info("Manual weight entry as parameter")
        if not isfloat(args.weight):
            logging.info("Received weight is not a floating-point number.")
            print("Received weight is not a floating-point number.")
            parser.print_help()
            sys.exit()
        else:
            logging.info("Received weight is floating-point number.")
            user_weight = args.weight

    # Write the weight to Wahoo
    wahoo_api.write_weight_wahoo(user_weight)

    # Write the weight to intervals.icu
    intervals_api.set_intervals_weight(user_weight)

    # Write the weight to Strava
    strava_api.set_strava_weight(user_weight)

    sys.exit()


def set_logging_debug():
    ''' Logging level switching to debug '''
    logging.basicConfig(
        filename="weightsync.log", encoding="utf-8", level=logging.DEBUG
    )


def isfloat(num):
    ''' Check if num is a floating-point '''
    try:
        float(num)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    sys.exit(main())
