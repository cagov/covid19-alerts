chart_tests = [
    {
        'nom':'DATE_SUMMARY',
        'url':'https://covid19.ca.gov/state-dashboard',
        'pat':r'<p class="small-text">Last updated\&nbsp;(.*?) at',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'tracker-boxes',
    },
    # {
    #     'nom':'DATE_DASHBOARD',
    #     'url':'https://covid19.ca.gov/state-dashboard',
    #     'pat':r'<p class="small-text">(?:Updated|Vaccines administered updated) (.*?) at',
    #     'test_type':'DATE_MATCHES_TODAY',
    #     'bnom':'update-date',
    # },
    # {
    #     'nom':'DATE_CASES',
    #     'json_url':'https://data.covid19.ca.gov/data/dashboard/confirmed-cases/california.json?x=aa',
    #     'json_field':'meta.PUBLISHED_DATE',
    #     'test_type':'DATE_MATCHES_TODAYSNOW',
    #     'bnom':'cases-chart',
    # },
    {
        'nom':'MATCH_CASES_TOTAL',
        'url':'https://covid19.ca.gov/state-dashboard',
        'pat':r'<div id="total-cases-number" .*?<strong>(.*?)</strong',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/confirmed-cases/california.json?x=bb',
        'json_field':'data.latest.CONFIRMED_CASES.total_confirmed_cases',
        'test_type':'NUMBER_MATCHES_JSON',
        'bnom':'cases-chart',
    },
    # {
    #     'nom':'DATE_DEATHS',
    #     'json_url':'https://data.covid19.ca.gov/data/dashboard/confirmed-deaths/california.json?x=cc',
    #     'json_field':'meta.PUBLISHED_DATE',
    #     'test_type':'DATE_MATCHES_TODAYSNOW',
    #     'bnom':'deaths-chart',
    # },
    {
        'nom':'MATCH_DEATHS_TOTAL',
        'url':'https://covid19.ca.gov/state-dashboard',
        'pat':r'<div id="total-deaths-number" .*?<strong>(.*?)</strong',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/confirmed-deaths/california.json?x=dd',
        'json_field':'data.latest.CONFIRMED_DEATHS.total_confirmed_deaths',
        'test_type':'NUMBER_MATCHES_JSON',
        'bnom':'deaths-chart',
    },
    # {
    #     'nom':'DATE_TESTS',
    #     'json_url':'https://data.covid19.ca.gov/data/dashboard/total-tests/california.json?x=ee',
    #     'json_field':'meta.PUBLISHED_DATE',
    #     'test_type':'DATE_MATCHES_TODAYSNOW',
    #     'bnom':'tests-chart',
    # },
    {
        'nom':'MATCH_TESTS',
        'test_type':'PASS', # no longer used
    },
    {
        'nom':'DATE_GROUPS',
        'json_url':'https://data.covid19.ca.gov/data/infections-by-group/infections-by-group-california.json?x=mm',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'groups-chart',
    },
    # {
    #     'nom':'DATE_POSITIVITY',
    #     'json_url':'https://data.covid19.ca.gov/data/dashboard/positivity-rate/california.json?x=nn',
    #     'json_field':'meta.PUBLISHED_DATE',
    #     'test_type':'DATE_MATCHES_TODAYSNOW',
    #     'bnom':'positivity-chart',
    # },
    # {
    #     'nom':'DATE_PATIENTS',
    #     'json_url':'https://data.covid19.ca.gov/data/dashboard/patients/california.json?x=ff ',
    #     'json_field':'meta.PUBLISHED_DATE',
    #     'test_type':'DATE_MATCHES_TODAYSNOW',
    #     'bnom':'patients-chart',
       
    # },
    # {
    #     'nom':'DATE_ICUBEDS',
    #     'json_url':'https://data.covid19.ca.gov/data/dashboard/icu-beds/california.json?x=gg',
    #     'json_field':'meta.PUBLISHED_DATE',
    #     'test_type':'DATE_MATCHES_TODAYSNOW',
    #     'bnom':'icu-beds-chart',
    # },
    {
        'nom':'DATE_VACCINE_SPARKLINES_DATA',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/vaccines/sparkline.json?x=hh',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'vaccines-sparklines-data',
    },
    {
        'nom':'SPARKLINE_CASES',
        'url':'http://files.covid19.ca.gov/img/generated/sparklines/sparkline-cases.svg?x=ii',
        'pat':r'RENDER_DATE:\s*(\d\d\d\d-\d\d-\d\d)',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'cases-sparkline',
    },
    {
        'nom':'SPARKLINE_DEATHS',
        'url':'http://files.covid19.ca.gov/img/generated/sparklines/sparkline-deaths.svg?x=jj',
        'pat':r'RENDER_DATE:\s*(\d\d\d\d-\d\d-\d\d)',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'deaths-sparkline',
    },
    {
        'nom':'SPARKLINE_TESTS',
        'url':'http://files.covid19.ca.gov/img/generated/sparklines/sparkline-tests.svg?x=kk',
        'pat':r'RENDER_DATE:\s*(\d\d\d\d-\d\d-\d\d)',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'tests-sparkline',
    },
    {
        'nom':'SPARKLINE_VACCINES',
        'url':'http://files.covid19.ca.gov/img/generated/sparklines/sparkline-vaccines.svg?x=ll',
        'pat':r'RENDER_DATE:\s*(\d\d\d\d-\d\d-\d\d)',
        'test_type':'DATE_MATCHES_TODAYSNOW',
        'bnom':'vaccines-sparkline',
    },
    {
        'nom':'DATE_POSTVAX',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/postvax/california.json?x=xx',
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
