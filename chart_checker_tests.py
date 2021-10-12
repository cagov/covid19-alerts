chart_tests = [
    {
        'nom':'DATE_SUMMARY',
        'url':'https://covid19.ca.gov/state-dashboard',
        'pat':r'<p class="small-text">Last updated\&nbsp;(.*?) at',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'summaries',
    },
    {
        'nom':'DATE_CASES',
        'json_url':'https://files.covid19.ca.gov/data/dashboard/confirmed-cases/california.json?x=x',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'cases',
    },
    {
        'nom':'MATCH_CASES_TOTAL',
        'url':'https://covid19.ca.gov/state-dashboard',
        'pat':r'<div id="total-cases-number" .*?<strong>(.*?)</strong',
        'json_url':'https://files.covid19.ca.gov/data/dashboard/confirmed-cases/california.json?x=x',
        'json_field':'data.latest.CONFIRMED_CASES.total_confirmed_cases',
        'test_type':'NUMBER_MATCHES_JSON',
        'bnom':'cases',
    },
    {
        'nom':'DATE_DEATHS',
        'json_url':'https://files.covid19.ca.gov/data/dashboard/confirmed-cases/california.json?x=x',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'deaths',
    },
    {
        'nom':'MATCH_DEATHS_TOTAL',
        'url':'https://covid19.ca.gov/state-dashboard',
        'pat':r'<div id="total-deaths-number" .*?<strong>(.*?)</strong',
        'json_url':'https://files.covid19.ca.gov/data/dashboard/confirmed-deaths/california.json?x=x',
        'json_field':'data.latest.CONFIRMED_DEATHS.total_confirmed_deaths',
        'test_type':'NUMBER_MATCHES_JSON',
        'bnom':'deaths',
    },
    {
        'nom':'DATE_TESTS',
        'json_url':'https://files.covid19.ca.gov/data/dashboard/confirmed-cases/california.json?x=x',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'tests',
    },
    {
        'nom':'MATCH_TESTS',
        'test_type':'PASS', # no longer used
    },
    {
        'nom':'DATE_GROUPS',
        'json_url':'https://files.covid19.ca.gov/data/infections-by-group/infections-by-group-california.json',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'groups',
    },
    {
        'nom':'DATE_POSITIVITY',
        'json_url':'https://files.covid19.ca.gov/data/dashboard/positivity-rate/california.json?x=x',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'positivity',
    },
    {
        'nom':'DATE_PATIENTS',
        'json_url':'https://files.covid19.ca.gov/data/dashboard/patients/california.json?x=x ',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'patients',
       
    },
    {
        'nom':'DATE_ICUBEDS',
        'json_url':'https://files.covid19.ca.gov/data/dashboard/icu-beds/california.json?x=x',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'icu-beds',
    },
    {
        'nom':'DATE_VACCINE_SPARKLINES_DATA',
        'json_url':'https://files.covid19.ca.gov/data/dashboard/vaccines/sparkline.json?x=x',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'vaccines-sparklines-data',
    },
    {
        'nom':'SPARKLINE_CASES',
        'url':'https://files.covid19.ca.gov/img/generated/sparklines/sparkline-cases.svg',
        'pat':r'DATA_PUBLISHED_DATE:\s*(.*?)\s*,',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'cases-sparkline',
    },
    {
        'nom':'SPARKLINE_DEATHS',
        'url':'https://files.covid19.ca.gov/img/generated/sparklines/sparkline-deaths.svg',
        'pat':r'DATA_PUBLISHED_DATE:\s*(.*?)\s*,',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'deaths-sparkline',
    },
    {
        'nom':'SPARKLINE_TESTS',
        'url':'https://files.covid19.ca.gov/img/generated/sparklines/sparkline-tests.svg',
        'pat':r'DATA_PUBLISHED_DATE:\s*(.*?)\s*,',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'tests-sparkline',
    },
    {
        'nom':'SPARKLINE_VACCINES',
        'url':'https://files.covid19.ca.gov/img/generated/sparklines/sparkline-vaccines.svg',
        'pat':r'DATA_PUBLISHED_DATE:\s*(.*?)\s*,',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'vaccines-sparkline',
    },
    {
        'nom':'DATE_POSTVAX',
        'json_url':'https://files.covid19.ca.gov/data/dashboard/postvax/california.json?x=x',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'WEEKDATE_GTE_WEDNESDAY',
        'bnom':'postvax-charts',
    },
]


'''

DATE_MATCHES_TODAY
 match against now.strftime('%B %-d, %Y')

DATE_MATCHES_TODAYSNOW
 pull date from either json_url/json_field (if present) or url/pat
 match against now.strftime('%Y-%m-%d')

WEEKDATE_GTE_WEDNESDAY
 pull date from either json_url/json_field (if present) or url/pat
 check if it's >= date of most recent wednesday (including today)
 normally this will only fail for a weekly file on wednesday morning.

NUMBER_MATCHES_JSON
 pull number from html, remove commas and convert to int
 pull number from json
 compare

 PASS - force pass (used for old tests)

Automatically build masks using DATE tests and non-date tests..

'''
