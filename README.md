# AppsFlyer Data Source (Extractor)
Appsflyer is a mobile attribution and marketing analytics platform that helps app marketers measure the performance of their mobile campaigns across all channels.

This component allows users to extract report data via the [Appsflyer API](https://support.appsflyer.com/hc/en-us/articles/207034346-Pull-APIs-Pulling-AppsFlyer-Reports-by-APIs#Raw)

## Prerequisites

To use this component you will need an AppsFlyer API token. To get your API token, go to the [API Token section in the Security settings in AppsFlyer](https://hq1.appsflyer.com/account/api-tokens) and copy the *API token V2.0*

## Defining reports

You can download multiple reports with the component, and each has to be configured separately.

Each report must have a defined Report Name, these are defined by AppsFlyer in their [documentation](https://dev.appsflyer.com/hc/reference/overview-5)

The available report types are listed in the following subcategories:

### Raw Data Reports (non-organic)
* Installs Report (installs_report) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-installs-report-v5)
* In-app events Report (in_app_events_report) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-in-app-events-report-v5)
* Uninstalls Report (uninstall_events_report) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-uninstall-events-report-v5)
* Reinstalls Report (reinstalls) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-reinstalls-v5)

### Raw Data Reports (organic)
* Organic Installs Report (organic_installs_report) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-organic-installs-report-v5)
* Organic in-app events Report (organic_in_app_events_report) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-organic-in-app-events-report-v5)
* Organic uninstalls Report (organic_uninstall_events_report) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-organic-uninstall-events-report-v5)
* Organic reinstalls Report (reinstalls_organic) -Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-reinstalls-organic-v5) 

### Retargeting
* Conversions (re-engagements & re-attributions) Report (installs-retarget) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-installs-retarget-v5)
* In-app events Report (in-app-events-retarget) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-in-app-events-retarget-v5)

### Ad revenue raw data 
* Attributed ad revenue Report (ad_revenue_raw) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-ad-revenue-raw-v5)
* Organic ad revenue Report (ad_revenue_organic_raw) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-ad-revenue-organic-raw-v5)
* Retargeting ad revenue Report (ad-revenue-raw-retarget) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-ad-revenue-raw-retarget-v5)


### Protect360 fraud
* Installs Report (blocked_installs_report) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-blocked-installs-report-v5)
* Post-attribution installs Report (detection) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-detection-v5)
* In-app events Report (blocked_in_app_events_report) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-blocked-in-app-events-report-v5)
* Post-attribution in-app events Report (fraud-post-inapps) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-fraud-post-inapps-v5)
* Clicks Report (blocked_clicks_report) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-blocked-clicks-report-v5)
* Blocked install postbacks Report (blocked_install_postbacks) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-blocked-install-postbacks-v5)

### Postbacks
* Install postbacks Report (postbacks) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-postbacks-v5)
* In-app event postbacks Report (in-app-events-postbacks) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-in-app-events-postbacks-v5)
* Retargeting in-app event postbacks Report (retarget_in_app_events_postbacks) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-retarget-in-app-events-postbacks-v5)
* Retargeting conversions postbacks Report (retarget_install_postbacks) - Report described in [AppsFlyer report documentation](https://dev.appsflyer.com/hc/reference/get_app-id-retarget-install-postbacks-v5)

Once you select a report you must specify the following required parameters:

* **Application ID/s**, fill in multiple application IDs by separating them by columns, e.g. app1, app2, app3
* **Start** and **End date**, these 2 parameters define the range of the report you which you wish to download. you can use either absolute dates YYYY-MM-DD or relative dates like < today, yesterday, 7 days ago etc, in 3 days. 

Furthermore, you can set the following optional parameters:

* **Primary Keys**, you can specify which columns should be used as Primary Key. Please provide these in this format `column_1, column_2, column_3` (list the names and separate them with a comma).
* **Attribute to retargeting campaigns** (only use if you are still using the V1 API (deprecated by 31.5.2023)) you can convert this option to true to get results attributed to retargeting campaigns.
* **Filter by event name** (to be used for reports with events) - set Event ID/s. To filter multiple events use a comma separated list of events.
* **Filter by media source** media_source: Use to filter the call for a specific media source. Set both the media_source and category parameters as follows: For Facebook set category and media_source to facebook, For Twitter set category and media_source to twitter,
For all other media sources set category to standard and media_source to the name of the media source.
* **Report intervals** In case your date ranges create more than 200K rows, you must split the downloading into multiple intervals. If for example you download data from the past 2 weeks, and set intervals to 2, the data will be fetched in 2 intervals, each 1 week long.


### Sample Configuration

```json
{

  "parameters": {
    "token_type": "v2",
    "#api_token_v2": "YOUR_API_TOKEN_HERE",
    "reports": [
      {
        "name": "installs_report",
        "Primary Key": "AppsFlyer_ID, Install_Time, Media_Source, Campaign, Event_Name, Event_Time, Event_Value",
        "reattr": false,
        "from_dt": "1 week ago",
        "Application IDs": "myapp1, myapp2",
        "filter_by_event_name": [],
        "to_dt": "yesterday",
        "filter_by_media_source": [
          {
            "category": "facebook",
            "media_source": "facebook"
          }
        ],
        "date_intervals": 1
      }
    ]
  },
  "action": "run"
}

```


## Output
The component creates one table in storage per each report with data from all the specified Applications. The load is incremental. The Primary Key is set to these columns in default, but it can be changed: `AppsFlyer_ID, Install_Time, Media_Source, Campaign, Event_Name, Event_Time, Event_Value`

