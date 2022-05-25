from dataclasses import dataclass
from typing import List, Dict
from keboola.utils.helpers import comma_separated_values_to_list


@dataclass
class AppsflyerReport:
    report_name: str
    app_id: str
    attribute_to_retargeting: bool
    filter_by_event_name: List[str]
    filter_by_media_source: List[str]
    primary_keys: List[str]


def create_report_object(report_dict: Dict, app_id: str) -> AppsflyerReport:
    report_name = report_dict.get("name")
    app_id = app_id
    filter_by_event_name = report_dict.get("filter_by_event_name")
    filter_by_media_source = report_dict.get("filter_by_media_source")
    attribute_to_retargeting = report_dict.get("reattr")
    primary_keys = comma_separated_values_to_list(report_dict.get("Primary Key"))
    return AppsflyerReport(report_name=report_name, app_id=app_id, attribute_to_retargeting=attribute_to_retargeting,
                           filter_by_event_name=filter_by_event_name, filter_by_media_source=filter_by_media_source,
                           primary_keys=primary_keys)
