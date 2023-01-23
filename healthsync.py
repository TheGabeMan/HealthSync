"""
    config section
"""

# from genericpath import isfile
import sys
import logging
import getopt
import wahoo_api
import strava_api
import intervals_api


logging.basicConfig(filename='weightsync.log',
                    encoding='utf-8',
                    level=logging.INFO)
'''
    logging.debug('This message should go to the log file')
    logging.info('So should this')
    logging.warning('And this, too')
    logging.error('And non-ASCII stuff, too, like Øresund and Malmö')
'''


"""
    Start of main script
"""


def main():

    arg_options = check_arguments(sys.argv)

    if "--weight" in arg_options[0]:
        print("Manual weight entry")
        for i in range(len(arg_options)):
            if arg_options[i][0] == '--weight':
                user_weight = arg_options[i][1]
                # Write the weight to Wahoo
                wahoo_api.write_weight_wahoo(user_weight)

                # Write the weight to intervals.icu
                intervals_api.set_intervals_weight(user_weight)

                # Write the weight to Strava
                strava_api.set_strava_weight(user_weight)

    sys.exit()


'''
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
        withings_measurements = get_withings_measurements(withings_access_token)
        print('***********    WITHINGS    DATA ***********')
        print("Withings data:\n\r",withings_measurements)
        exit()
'''


def check_arguments(arguments):
    # TODO: Switch to ArgParse ( https://realpython.com/command-line-interfaces-python-argparse/ )
    try:
        opts, args = getopt.getopt(arguments[1:],
                                   "",
                                   ["debug", "weight="]
                                   )
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        logging.info(err)
        usage()
        sys.exit(2)

    return_value = []
    for opt in opts:
        if opt[0] == "--weight":
            logging.debug('Weight from cmdline: %s' % opt[1])
            if not isfloat(opt[1]):
                logging.debug('Received weight is not a floating-point number.')
                print("Received weight is not a floating-point number.")
                usage()
                sys.exit()
            else:
                logging.debug('Received weight is floating-point number.')
                return_value.append([opt[0], opt[1]])
        else:
            logging.debug('Received opt is not matched.')
            usage()

    for arg in args:
        if arg == "debug":
            set_logging_debug()
    return return_value


def set_logging_debug():
    logging.basicConfig(filename='weightsync.log',
                        encoding='utf-8',
                        level=logging.DEBUG)


def isfloat(num):
    # Check if num is a floating-point
    try:
        float(num)
        return True
    except ValueError:
        return False


def usage():
    print('Run script as: healthsync.py --help --weight <weight in kg> --withings')
    print('--weight <kg>    manual weight input in KG, will be synced to other applications')
    print('--withings   sync data from withings to other applications')
    print('--verbose    verbose logging on')


if __name__ == "__main__":
    exit(main())
