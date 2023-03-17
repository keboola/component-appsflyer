from keboola.http_client import HttpClient
from requests import HTTPError
from typing import List, Dict
from requests.exceptions import RetryError
import requests
import logging

BASE_URL = "https://hq.appsflyer.com/export/"

API_VERSION = "v5"

MAX_TIMEOUT_FOR_REQUEST = 1000


class AppsFlyerClientException(Exception):
    pass


class AppsFlyerClient(HttpClient):
    def __init__(self, api_token: str) -> None:
        self.api_token = api_token
        super().__init__(BASE_URL, max_retries=5, status_forcelist=(500, 502, 504))

    def get_app_daily_report(self,
                             report_name: str,
                             app_id: str,
                             date: Dict,
                             attribute_to_retargeting: bool,
                             filter_by_event_name: List,
                             filter_by_media_source: List) -> requests.Response:
        query_params = {
            "api_token": self.api_token,
            "from": date.get("start_date"),
            "to": date.get("end_date")
        }
        endpoint = "/".join([app_id, report_name, API_VERSION])

        if len(filter_by_event_name) > 0:
            query_params["event_name"] = filter_by_event_name[0]['event_name'].replace(' ', '')

            # Media Source
        if len(filter_by_media_source) > 0:
            category = filter_by_media_source[0]['category']
            media_source = filter_by_media_source[0]['media_source']
            if category == '' or media_source == '':
                raise AppsFlyerClientException("Media's category and media_source cannot be empty.")
            query_params["category"] = category
            query_params["media_source"] = media_source

        if attribute_to_retargeting:
            query_params["reattr"] = "true"

        try:
            report = self.get_raw(endpoint_path=endpoint, params=query_params, timeout=MAX_TIMEOUT_FOR_REQUEST)
        except (HTTPError, RetryError) as http_error:
            raise AppsFlyerClientException(http_error) from http_error

        if report.status_code == 404:
            query_params["api_token"] = "API TOKEN IS HIDDEN FROM LOG"
            raise AppsFlyerClientException(
                f"Error occurred : {report.reason}. Make sure report parameters are set correctly.\n"
                f"Check if App ID '{app_id}' is valid.\n"
                f"Check if query_params are valid {query_params}")
        elif report.status_code == 401:
            logging.error(report.text)
            raise AppsFlyerClientException(f"Error occurred : {report.reason} when fetching {endpoint} endpoint."
                                           f"Check if your API token is valid")
        elif report.status_code not in [200]:
            raise AppsFlyerClientException(f"Error occurred : {report.reason}. {report.text}")

        return report
