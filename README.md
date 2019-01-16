# ex-marketo

Keboola Connection docker app for extracting data from specific endpoints of Marketo REST API. Available under `radim-kasparek.ex-marketo`


## Functionality
This component allows KBC to get data from a few endpoints of the Marketo REST API (http://developers.marketo.com/rest-api/). 
It relies heavily on package marketorestpython (https://github.com/jepcastelein/marketo-rest-python).

As of now, the component can be used for extracting data from 5 endpoints, but it can be easily extended:
- extract_leads_by_ids
- extract_leads_by_filter
- get_lead_activities
- get_lead_changes
- get_deleted_leads
- get_campaigns
- get_activity_types

## Parameters
There are 10 options in the UI:
- Munchkin ID
- Client ID
- Client Secret
- Input/Output tables. *The tables need to mapped to specific names (names can be found in main.py)*
- Desired Fields. *write down the column names you want to extract and separate them by white space*
- Method. *denotes the endpoint*
- Until Date
- Since Date
- Column with Filter Values *Denotes the column in the input file that contains the values you want to filter for*
- Field to filter on *Denotes the field in the API to filter on*
- How many days back you want to go? *Alternative to Since Date. The Until Date is automatically set to current date if this field is used.*

## Endpoints
- extract_leads_by_ids
    * Takes in _Desired Fields_ parameter
    * The output is mapped to `leads_by_ids`
    * The input needs to contain column with name `lead_id` with list of id
    * The _Desired Fields_ parameter denotes which fields should be retrieved
- extract_leads_by_filter
    * Takes in _Desired Fields_ and _Column with Filter Values_ parameter
    * The output is mapped to `leads_by_filter`
    * The input needs to contain column with the values to input to the filter (the column is specified by the _Filter Values Column_)
    * The _Desired Fields_ parameter denotes which fields should be retrieved
    * Current functionality allows only filtering on e-mail
- get_lead_activities
    * Takes in _Since Date_ and _Until_date_ parameter. These denote the date when the activity occured.
    * The output is mapped to `lead_activites`
    * The input needs to contain columns 'activity_type_ids' and 'lead_ids'
    * output file will contain columns based on the fields in extracted responses 
    * it can definitely happen that different runs will produce different number of columns!!
    * _Since Date_ and _until_date_ parameters are self-explanatory
- get_lead_changes
    * Takes in _Since Date, Until Date_ and _Desired Fields_ parameter. These denote the date of the change in a lead.
    * The output is mapped to `lead_changes`
    * Output file will contain columns `leadId`, `activityDate` and `activityTypeId`
    * _Since Date_  and _Until Date_ parameters are self-explanatory
    * _Desired Fields_ parameter denotes the list of field names to return changes for, field names can be retrieved with the Describe Lead API
- get_deleted_leads
    * Takes in the _Since Date_ parameter. This denotes the date when a lead was deleted.
    * The output is mapped to `deleted_leads`
- get_campaigns
    * Takes in the _Field to filter on_ and _Column with Filter Values_
    * If the above parameters are left blank, all campaigns are retrieved.
    * The output is mapped to `campaigns`
- get_activity_types
    * Doesn't require any parameters.
    * The output is mapped to `activity_types`.
    





