# ex-appsflyer

Keboola Connection docker app for extracting data from AppsFlyer API. Available under `kds-team.ex-appsflyer`.


## Functionality
This component allows KBC to get data from the Appsflyer API (https://support.appsflyer.com/hc/en-us/articles/207034346-Pull-APIs-Pulling-AppsFlyer-Reports-by-APIs#Raw). 

## Parameters
There are 5 options in the UI:
- API token
- Report Name *This will be pasted into the target URL, so e.g. for Installs Reports please use installs_reports, as specified in the online documenentation*
- Application IDs *Write down the Application IDs and separate those by commas*
- Start Date *you can use either absolute dates YYYY-MM-DD or relative dates like < today, yesterday, 7 days ago etc, in 3 days. > For complete list of dates the component accepts please refer here: https://github.com/scrapinghub/dateparser"*
- End Date *you can use either absolute dates YYYY-MM-DD or relative dates like < today, yesterday, 7 days ago etc, in 3 days. > For complete list of dates the component accepts please refer here: https://github.com/scrapinghub/dateparser"*

The latter 4 are grouped in so-called object. Please specify one object per one report you want to extract.
## Output
The component creates one table in storage per each report with data from all the specified Applications. The load is incremental, as the Primary Key are used these columns: AppsFlyer_ID, Install_Time, Media_Source, Campaign, Event_Name, Event_Time, Event_Value.

