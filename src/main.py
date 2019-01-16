import os
from keboola import docker
import urllib.request
import urllib.parse
import urllib.error
import logging
import sys
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

sys.tracebacklimit = None

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")

# Access the supplied rules
cfg = docker.Config('/data/')
params = cfg.get_parameters()
logging.info("params read")

# Get the parameters
desired_reports_tmp = cfg.get_parameters()["desired_reports"]
from_dt = cfg.get_parameters()["from_date"]  # YYYY-MM-DD
to_dt = cfg.get_parameters()["to_date"]  # YYYY-MM-DD
api_endpoint = cfg.get_parameters()["#api_endpoint"]
api_token = cfg.get_parameters()["api_token"]
app_id_tmp = cfg.get_parameters()["app_id"]
dayspan = int(cfg.get_parameters()["dayspan"])
desired_reports = [i.strip() for i in desired_reports_tmp.split(",")]
app_ids = [i.strip() for i in app_id_tmp.split(",")]
logging.info("config successfuly read")


if (from_dt != '' or to_dt != '') and dayspan != '':
    logging.error("Please add either From Date and To Date, or dayspan, not both.")
    sys.exit(1)
elif (from_dt == '' or to_dt == '') and dayspan == '':
    logging.error("Please add either From Date and To Date or dayspan.")
    sys.exit(1)
elif (from_dt != '' and to_dt != '') and dayspan == '':
    pass
elif (from_dt == '' or to_dt == '') and dayspan != '':
    to_dt = datetime.today().strftime('%Y-%m-%d')
    from_dt = (datetime.utcnow() - timedelta(days = int(dayspan)))\
        .date().isoformat()

# Destination to fetch and output files and tables
DEFAULT_TABLE_INPUT = "/data/in/tables/"
DEFAULT_FILE_INPUT = "/data/in/files/"

DEFAULT_FILE_DESTINATION = "/data/out/files/"
DEFAULT_TABLE_DESTINATION = "/data/out/tables/"


def get_n_export_one_report(api_endpoint, api_token, app_id, report_name, from_date, to_date):
    query_params = {
        "api_token": api_token,
        "from": str(from_date),
        "to": str(to_date)
    }

    query_string = urllib.parse.urlencode(query_params)

    request_url = api_endpoint + app_id + "/" + report_name + "/v5?" + query_string

    logging.info('Sending request to: ' + request_url)

    try:
        resp = urllib.request.urlopen(request_url)
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
        "appsflyer_" + report_name + "_" + app_id + ".csv"
    with open(output_file, "wb") as out_file:
        out_file.write(resp.read())

        cfg.write_table_manifest(file_name=output_file,
                                 destination='',
                                 primary_key=['AppsFlyer ID', 'Install Time', 'Media Source',
                                              'Campaign', 'Event Name', 'Event Time', 'Event Value'],
                                 incremental=True)

# main


def main():

    for app_id in app_ids:
        for report_name in desired_reports:

            get_n_export_one_report(api_endpoint=api_endpoint, api_token=api_token,
                                    app_id=app_id, report_name=report_name, from_date=from_dt, to_date=to_dt)

            logging.info('Report ' + report_name + ' for app_id ' +
                         app_id + ' succesfully fetched.')

        logging.info('All reports for ' + app_id + ' succesfully_fetched')

    logging.info('All reports fetched')


if __name__ == "__main__":
    main()

    logging.info("Done.")
