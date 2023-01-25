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

    if args.weight:
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


"""
    elif len(sys.argv) > 1 and sys.sys.argv[1] == 'withings':
        withings_access_token = (
            withings_refresh(json.load(open(withings_cfg)))
            if os.path.isfile(withings_cfg)
            else withings_authenticate()
        )

        # Read from intervals.icu the last 30 days of wellness data
        icu_wellness_data = get_intervals_wellness()
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
        withings_measurements = 
                get_withings_measurements(withings_access_token)
        print('***********    WITHINGS    DATA ***********')
        print("Withings data:\n\r",withings_measurements)
        exit()
"""


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
    exit(main())
