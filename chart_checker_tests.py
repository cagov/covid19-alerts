
# note: monday is 0, Sunday is 6
weekdays_only   = [1,1,1,1,1,0,0]
tue_fri_only    = [0,1,0,0,1,0,0]
fri_only        = [0,0,0,0,1,0,0]
all_days        = [1,1,1,1,1,1,1]
no_stale_days   = [0,0,0,0,0,0,0]
wednesday_stale = [0,0,1,0,0,0,0]
thursday_stale  = [0,0,0,1,0,0,0]
friday_stale    = [0,0,0,0,1,0,0]

chart_tests = [
    {
        'nom':'DATE_SUMMARY',
        'url':'https://covid19.ca.gov/state-dashboard',
        'pat':r'<p class="small-text">Last updated\&nbsp;(.*?) at',
        'test_type':'DATE_MATCHES_TODAY',
        'active_days': tue_fri_only,
        'bnom':'tracker-boxes',
    },
    {
        'nom':'DATE_DASHBOARD',
        'url':'https://covid19.ca.gov/state-dashboard',
        'pat':r'<p class="small-text">(?:Updated|Vaccines administered updated) (.*?) at',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'update-date',
        'active_days': tue_fri_only,
        'not-on-holidays':True,
    },
    {
        'nom':'DATE_CASES',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/confirmed-cases/california.json?x=aa',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'cases-chart',
        'active_days': tue_fri_only,
        'not-on-holidays':True,
    },
    {
        'nom':'MATCH_CASES_TOTAL',
        'url':'https://covid19.ca.gov/state-dashboard',
        'pat':r'<div id="total-cases-number" .*?<strong>(.*?)</strong',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/confirmed-cases/california.json?x=bb',
        'json_field':'data.latest.CONFIRMED_CASES.total_confirmed_cases',
        'test_type':'NUMBER_MATCHES_JSON',
        'bnom':'cases-chart',
        'active_days': tue_fri_only,
    },
    {
        'nom':'DATE_DEATHS',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/confirmed-deaths/california.json?x=cc',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'deaths-chart',
        'active_days': tue_fri_only,
        'not-on-holidays':True,
    },
    {
        'nom':'MATCH_DEATHS_TOTAL',
        'url':'https://covid19.ca.gov/state-dashboard',
        'pat':r'<div id="total-deaths-number" .*?<strong>(.*?)</strong',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/confirmed-deaths/california.json?x=dd',
        'json_field':'data.latest.CONFIRMED_DEATHS.total_confirmed_deaths',
        'test_type':'NUMBER_MATCHES_JSON',
        'bnom':'deaths-chart',
        'active_days': all_days,
    },
    {
        'nom':'DATE_TESTS',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/total-tests/california.json?x=ee',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'tests-chart',
        'active_days': tue_fri_only,
        'not-on-holidays':True,
    },
    {
        'nom':'MATCH_TESTS',
        'test_type':'PASS', # no longer used
    },
    {
        'nom':'DATE_GROUPS',
        'json_url':'https://data.covid19.ca.gov/data/infections-by-group/infections-by-group-california.json?x=mm',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'groups-chart',
        'active_days': tue_fri_only,
    },
    {
        'nom':'DATE_POSITIVITY',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/positivity-rate/california.json?x=nn',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'positivity-chart',
        'active_days': tue_fri_only,
        'not-on-holidays':True,
    },
    {
        'nom':'DATE_PATIENTS',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/patients/california.json?x=ff ',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'patients-chart',
        'active_days': tue_fri_only,
    },
    {
        'nom':'DATE_ICUBEDS',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/icu-beds/california.json?x=gg',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'icu-beds-chart',
        'active_days': tue_fri_only,
    },
    {
        'nom':'DATE_VACCINE_SPARKLINES_DATA',
        'json_url':'https://data.covid19.ca.gov/data/dashboard/vaccines/sparkline.json?x=hh',
        'json_field':'meta.PUBLISHED_DATE',
        'test_type':'DATE_MATCHES_TODAY',
        'bnom':'vaccines-sparklines-data',
        'active_days': tue_fri_only,
        'not-on-holidays':True,
    },
    {
        'nom':'DATE_SPARKLINE_CASES',
        'svg_url':'http://files.covid19.ca.gov/img/generated/sparklines/sparkline-cases.svg?x=ii',
        'test_type':'DATE_MATCHES_TODAY',
        'meta_field':'RENDER_DATE',
        'bnom':'cases-sparkline',
        'active_days': tue_fri_only,
    },
    {
        'nom':'DATE_SPARKLINE_DEATHS',
        'svg_url':'http://files.covid19.ca.gov/img/generated/sparklines/sparkline-deaths.svg?x=jj',
        'test_type':'DATE_MATCHES_TODAY',
        'meta_field':'RENDER_DATE',
        'bnom':'deaths-sparkline',
        'active_days': tue_fri_only,
    },
    {
        'nom':'DATE_SPARKLINE_TESTS',
        'svg_url':'http://files.covid19.ca.gov/img/generated/sparklines/sparkline-tests.svg?x=kk',
        'test_type':'DATE_MATCHES_TODAY',
        'meta_field':'RENDER_DATE',
        'bnom':'tests-sparkline',
        'active_days': tue_fri_only,
    },
    {
        'nom':'DATE_SPARKLINE_VACCINES',
        'svg_url':'http://files.covid19.ca.gov/img/generated/sparklines/sparkline-vaccines.svg?x=ll',
        'test_type':'DATE_MATCHES_TODAY',
        'meta_field':'RENDER_DATE',
        'bnom':'vaccines-sparkline',
        'active_days': tue_fri_only,
    },
    # enable these again next week
    # {
    #     'nom':'DATE_POSTVAX',
    #     'json_url':'https://data.covid19.ca.gov/data/dashboard/postvax/california.json?x=xx',
    #     'json_field':'meta.PUBLISHED_DATE',
    #     'test_type':'DATE_WEEKLY_MATCH',
    #     'weekday': 4,
    #     'stale_days': friday_stale,
    #     'bnom':'postvax-charts',
    #     'active_days': all_days,
    # },
    # {
    #     'nom':'DATE_VARIANTS',
    #     'json_url':'https://data.covid19.ca.gov/data/variants/california.json?x=xx',
    #     'json_field':'meta.PUBLISHED_DATE',
    #     'test_type':'DATE_WEEKLY_MATCH',
    #     'weekday': 4,
    #     'stale_days': friday_stale,
    #     'bnom':'variant-chart',
    #     'active_days': all_days,
    # },
]


'''

DATE_MATCHES_TODAY
 match against now.strftime('%B %-d, %Y')

DATE_MATCHES_TODAY
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
