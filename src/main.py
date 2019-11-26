import os
from keboola import docker
import urllib.request
import urllib.parse
import urllib.error
import logging
import logging_gelf.handlers
import logging_gelf.formatters
import sys
import datetime
import dateparser
import json
"__author__ = 'Radim Kasparek kasrad'"
"__credits__ = 'Keboola Drak"
"__component__ = 'AppsFlyer Extractor'"

"""
Python 3 environment
"""


# Environment setup
abspath = os.path.abspath(__file__)
script_path = os.path.dirname(abspath)
os.chdir(script_path)

sys.tracebacklimit = 0

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")

if 'KBC_LOGGER_ADDR' in os.environ and 'KBC_LOGGER_PORT' in os.environ:

    logger = logging.getLogger()
    logging_gelf_handler = logging_gelf.handlers.GELFTCPSocketHandler(
        host=os.getenv('KBC_LOGGER_ADDR'),
        port=int(os.getenv('KBC_LOGGER_PORT'))
    )
    logging_gelf_handler.setFormatter(
        logging_gelf.formatters.GELFFormatter(null_character=True))
    logger.addHandler(logging_gelf_handler)

    # removes the initial stdout logging
    logger.removeHandler(logger.handlers[0])

# Access the supplied rules
cfg = docker.Config('/data/')
params = cfg.get_parameters()
logging.info("params read")
logging.info(params)

# Get the parameters
api_token = cfg.get_parameters()["#api_token"]
reports = cfg.get_parameters()["reports"]
logging.info("config successfuly read")


# Destination to fetch and output files and tables
DEFAULT_TABLE_INPUT = "/data/in/tables/"
DEFAULT_FILE_INPUT = "/data/in/files/"

DEFAULT_FILE_DESTINATION = "/data/out/files/"
DEFAULT_TABLE_DESTINATION = "/data/out/tables/"


def get_n_export_one_report(api_token, app_id, report_name, date, reattr, filter_by_event_name, filter_by_media_source):
    # from_date, to_date, reattr):
    '''
    function for getting and exporting one report per one app_id
    from_date - YYYY-MM-DD
    to_date - YYYY-MM-DD
    '''

    query_params = {
        "api_token": api_token,
        "from": str(date),
        "to": str(date)
    }

    query_string = urllib.parse.urlencode(query_params)
    # Handling Filters
    # Event Name
    if len(filter_by_event_name) > 0:
        event_names = '&event_name={}'.format(
            filter_by_event_name[0]['event_name'].replace(' ', ''))
        query_string = query_string + event_names

    # Media Source
    if len(filter_by_media_source) > 0:
        category = filter_by_media_source[0]['category']
        media_source = filter_by_media_source[0]['media_source']
        if category == '' or media_source == '':
            logging.error(
                'Media\'s category and media_source cannot be empty.')
            sys.exit(1)
        media_source_config = '&category={}&media_source={}'.format(
            category, media_source)
        query_string = query_string + media_source_config

    request_url = "https://hq.appsflyer.com/export/" + \
        app_id + "/" + report_name + "/v5?" + query_string

    # Adding the optino to attribute retargeting campaigns
    if bool(reattr):
        request_url = request_url + '&reattr=true'

    logging.info('Sending request to: ' + request_url)

    try:
        resp = urllib.request.urlopen(request_url)
        bytes_data = resp.read()
    except urllib.error.HTTPError as err:
        if err.code == 401:
            logging.error('Please check the API token.')
            sys.exit(1)
        elif err.code == 404:
            logging.error(
                'The page was not found. Please check the parameters.')
            sys.exit(1)
        else:
            logging.error('Error Code: {}'.format(err))
            sys.exit(1)

    if (len(bytes_data.decode("utf-8").splitlines())) == 0:
        return 1

    output_file = DEFAULT_TABLE_DESTINATION + \
        "appsflyer_" + report_name + '/' + app_id + "-{}.csv".format(date)
    logging.info(output_file)

    # writes the file without the first row, i.e. writes headless file
    with open(output_file, "w") as out_file:
        for line in bytes_data.decode("utf-8").splitlines()[1:]:
            out_file.write(line)
            out_file.write('\n')

    # returns the colnames of the file
    return str(bytes_data.decode("utf-8").splitlines()[0]).split(',')


def dates_request(start_date, end_date):
    """
    return a list of dates within the given parameters
    """
    dates = []
    three_months_limit = dateparser.parse('3 months ago')

    try:
        start_date_form = dateparser.parse(start_date)
        end_date_form = dateparser.parse(end_date)
        day_diff = (end_date_form-start_date_form).days

        # End date cannot exceed start_date
        if day_diff < 0:
            logging.error("ERROR: start_date cannot exceed end_date. ",
                          "Please correct your inputs.")
            sys.exit(1)
        # start date cannot exceed 3 months limit from today
        if start_date_form.strftime("%Y-%m-%d") < three_months_limit.strftime("%Y-%m-%d"):
            logging.error(
                "ERROR: API Querying date range is limited to past 3 months.")
            sys.exit(1)

        temp_date = start_date_form
        day_n = 0
        if day_diff == 0:
            dates.append(temp_date.strftime("%Y-%m-%d"))
        while day_n < day_diff:
            dates.append(temp_date.strftime("%Y-%m-%d"))
            temp_date += datetime.timedelta(days=1)
            day_n += 1
            if day_n == day_diff:
                dates.append(temp_date.strftime("%Y-%m-%d"))
    except TypeError:
        logging.error("ERROR: Please enter valid date parameters")
        sys.exit(1)

    return dates


def save_manifest(report_name, cols, primary_keys):
    """
    Dummy function for returning manifest
    """

    file = '/data/out/tables/' + "appsflyer_" + report_name + ".manifest"

    logging.info("Manifest output: {0}".format(file))

    manifest = {
        'destination': '',
        'columns': cols,
        'incremental': True,
        'primary_key': primary_keys
    }

    try:
        with open(file, 'w') as file_out:
            json.dump(manifest, file_out)
            logging.info("Output manifest file ({0}) produced.".format(file))
    except Exception as e:
        logging.error("Could not produce output file manifest.")
        logging.error(e)

    return

# main


def main():
    '''
    for each report the data from all apps are collected, written into the storage as sliced files
    and finally a manifest is produced
    '''
    for report in reports:
        # Report Parameters
        report_name = report['name']
        logging.info("Processing {} - {} to {}".format(report_name,
                                                       report['from_dt'], report['to_dt']))

        reattr = report['reattr']
        primary_keys = [i.strip() for i in report['Primary Key'].split(",")]
        app_ids = [i.strip() for i in report['Application IDs'].split(",")]
        date_list = dates_request(start_date=report['from_dt'],
                                  end_date=report['to_dt'])

        # Report Filter Parameters
        if 'filter_by_event_name' in report:
            filter_by_event_name = report['filter_by_event_name']
        else:
            filter_by_event_name = []
        if 'filter_by_media_source' in report:
            filter_by_media_source = report['filter_by_media_source']
        else:
            filter_by_media_source = []

        # Creating Folder for sliced files
        os.mkdir(DEFAULT_TABLE_DESTINATION + "/appsflyer_" + report_name)

        for app in app_ids:
            for date in date_list:
                c_names = get_n_export_one_report(api_token=api_token,
                                                  app_id=app,
                                                  report_name=report_name,
                                                  date=date,
                                                  reattr=reattr,
                                                  filter_by_event_name=filter_by_event_name,
                                                  filter_by_media_source=filter_by_media_source)
                if c_names == 1:
                    continue
                else:
                    colnames = c_names
        save_manifest(report_name=report_name, cols=colnames,
                      primary_keys=primary_keys)

        logging.info('Report ' + report_name + ' succesfully fetched.')
    logging.info('All reports fetched')


if __name__ == "__main__":
    main()

    logging.info("Done.")
