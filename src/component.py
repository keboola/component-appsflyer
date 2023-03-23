import logging
import warnings
import math
from os import path, mkdir
from datetime import timedelta, datetime
from typing import List, Generator, Dict
import keboola.utils.date as dutils
from keboola.utils.helpers import comma_separated_values_to_list
from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from appsflyer import AppsFlyerClient, AppsFlyerClientException, AppsflyerReport, create_report_object

KEY_API_TOKEN = '#api_token'
KEY_API_TOKEN_V2 = '#api_token_v2'
KEY_REPORTS = 'reports'

REQUIRED_PARAMETERS = []

warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)

DEFAULT_DATE_INTERVAL = 1


class Component(ComponentBase):
    def __init__(self):
        super().__init__()

    def run(self):
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)

        params = self.configuration.parameters
        api_token = params.get(KEY_API_TOKEN_V2, None)
        token_type = "v2" if api_token else "v1"
        api_token = api_token or params.get(KEY_API_TOKEN, None)
        if not api_token:
            raise UserException("API token V1 or V2 must be specified in config parameters.")

        reports = params.get(KEY_REPORTS, [])

        client = AppsFlyerClient(api_token, token_type)

        for report in reports:
            self.fetch_report(client, report)

    def fetch_report(self, client: AppsFlyerClient, report: Dict) -> None:
        report_name = report.get("name")
        if bool(report.get('reattr')):
            report_name = f"{report_name}_reattr"
        app_ids = comma_separated_values_to_list(report.get("Application IDs"))
        interval_days = self.get_date_intervals(report.get("from_dt"),
                                                report.get("to_dt"),
                                                report.get("date_intervals", DEFAULT_DATE_INTERVAL))

        logging.info(
            f"Fetching report {report_name} for period {interval_days[0].get('start_date')} - "
            f"{interval_days[-1].get('end_date')} with "
            f"intervals of {report.get('date_intervals', DEFAULT_DATE_INTERVAL)} days")

        for app_id in app_ids:
            report_object = create_report_object(report_dict=report, app_id=app_id)
            self.process_app_report(client, interval_days, report_object)

    def process_app_report(self,
                           client: AppsFlyerClient,
                           interval_days: List[Dict],
                           report: AppsflyerReport):
        out_table = f"appsflyer_{report.report_name}"
        table = self.create_out_table_definition(name=out_table,
                                                 incremental=True,
                                                 primary_key=report.primary_keys,
                                                 is_sliced=True)
        self.create_sliced_directory(table.full_path)

        for i, generated_report in enumerate(self.get_single_reports(client, interval_days, report)):
            output_file = path.join(table.full_path,
                                    f"{report.app_id}-{interval_days[i].get('start_date')}-"
                                    f"{interval_days[i].get('end_date')}.csv")
            table.columns = self.save_report(output_file, generated_report.text)
        self.write_manifest(table)

    @staticmethod
    def get_single_reports(client: AppsFlyerClient, intervals: List[Dict], report: AppsflyerReport) -> Generator:
        for interval in intervals:
            try:
                logging.info(f"Fetching report: {report.report_name} for app_id : {report.app_id} for range "
                             f"{interval.get('start_date')}- {interval.get('end_date')}")
                yield client.get_app_daily_report(report.report_name,
                                                  report.app_id,
                                                  interval,
                                                  report.attribute_to_retargeting,
                                                  report.filter_by_event_name,
                                                  report.filter_by_media_source)
            except AppsFlyerClientException as client_exc:
                raise UserException(client_exc) from client_exc

    @staticmethod
    def save_report(output_file_name: str, report_data: str) -> List[str]:
        with open(output_file_name, "w") as out_file:
            for line in report_data.splitlines()[1:]:
                out_file.write(line)
                out_file.write('\n')
            columns = report_data.splitlines()[0]
            # workaround for:
            # https://stackoverflow.com/questions/40310042/python-read-csv-bom-embedded-into-the-first-key
            columns = columns.split(",")
            if columns[0].startswith("\ufeff"):
                logging.info(f"Columns before fix: {columns}")
                columns[0].replace("\ufeff", "")
                logging.info(f"Columns after fix: {columns}")
        return columns

    @staticmethod
    def create_sliced_directory(table_path: str) -> None:
        if not path.isdir(table_path):
            mkdir(table_path)

    def get_date_intervals(self, date_from: str, date_to: str, date_intervals: str) -> List[Dict]:
        try:
            date_intervals = int(date_intervals)
        except ValueError as parse_error:
            raise UserException("Failed to parse date interval") from parse_error

        try:
            start_date, end_date = dutils.parse_datetime_interval(date_from, date_to)
        except TypeError as e:
            raise UserException("Failed to parse date to and from. Make sure the input is valid") from e

        return self.split_dates_to_chunks_no_overlap(start_date, end_date,
                                                     interval=date_intervals,
                                                     strformat='%Y-%m-%d')

    @staticmethod
    def split_dates_to_chunks_no_overlap(start_date: datetime, end_date: datetime,
                                         interval: int, strformat: str) -> List[Dict]:
        chunks = []
        delta = end_date - start_date
        single_days = [(start_date + timedelta(days=i)).strftime(strformat) for i in range(delta.days + 1)]
        interval = max(interval, 1)
        num_chunks = math.ceil(len(single_days) / interval)
        for i in range(num_chunks):
            start = i * interval
            end = start + interval - 1
            if end >= len(single_days):
                chunks.append({'start_date': single_days[start], 'end_date': single_days[-1]})
            else:
                chunks.append({'start_date': single_days[start], 'end_date': single_days[end]})

        return chunks


if __name__ == "__main__":
    try:
        comp = Component()
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
