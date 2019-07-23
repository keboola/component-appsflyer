import os
from keboola import docker
import urllib.request
import urllib.parse
import urllib.error
import logging
import sys
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


def get_n_export_one_report(api_token, app_id, report_name, from_date, to_date):
    '''
    function for getting and exporting one report per one app_id
    from_date - YYYY-MM-DD
    to_date - YYYY-MM-DD
    '''

    query_params = {
        "api_token": api_token,
        "from": str(from_date),
        "to": str(to_date)
    }

    query_string = urllib.parse.urlencode(query_params)

    request_url = "https://hq.appsflyer.com/export/" + \
        app_id + "/" + report_name + "/v5?" + query_string

    logging.info('Sending request to: ' + request_url)

    try:
        resp = urllib.request.urlopen(request_url)
        bytes_data = resp.read()
    except urllib.error.HTTPError as err:
        if err.code == 401:
            logging.info('Please check the API token.')
            sys.exit(1)
        elif err.code == 404:
            logging.info(
                'The page was not found. Please check the parameters.')
            sys.exit(1)
        else:
            logging.info('The error code is ' + str(err.code))
            sys.exit(1)

    output_file = DEFAULT_TABLE_DESTINATION + \
        "appsflyer_" + report_name + '/' + app_id + ".csv"
    logging.info(output_file)

    # writes the file without the first row, i.e. writes headless file
    with open(output_file, "w") as out_file:
        for line in bytes_data.decode("utf-8").splitlines()[1:]:
            out_file.write(line)
            out_file.write('\n')

    # returns the colnames of the file
    logging.info('The lenght of the first line is: ', str(len(
        bytes_data.decode("utf-8").splitlines())))
    return str(bytes_data.decode("utf-8").splitlines()[0]).split(',')


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
        report_name = report['name']
        primary_keys = report['Primary Key']
        from_dt = dateparser.parse(report['from_dt']).date()
        to_dt = dateparser.parse(report['to_dt']).date()
        app_ids = [i.strip() for i in report['Application IDs'].split(",")]
        os.mkdir(DEFAULT_TABLE_DESTINATION + "/appsflyer_" + report_name)
        for app in app_ids:
            c_names = get_n_export_one_report(api_token=api_token,
                                              app_id=app,
                                              report_name=report_name,
                                              from_date=from_dt,
                                              to_date=to_dt)
        save_manifest(report_name=report_name, cols=c_names,
                      primary_keys=primary_keys)

        logging.info('Report ' + report_name + ' succesfully fetched.')
    logging.info('All reports fetched')


if __name__ == "__main__":
    main()

    logging.info("Done.")
