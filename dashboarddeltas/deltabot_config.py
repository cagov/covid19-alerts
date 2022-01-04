# demandbot_config.py
trigger_factor = 2.0
deltabase_name = 'deltabase.json'
holidays = ['2022-01-03']
busy_sleep = 60*5
offhours_sleep = 60*60
# param order is:
# min_value, max_value, min_change, max_change, min_growth, max_growth

file_list = [
  {
    'filename': 'data/daily-stats-v2.json',
    'branch': 'CovidStateDashboard_Summary_Staging',
    'pdate_field': 'meta.PUBLISHED_DATE',
    'fields_of_interest': [
        {   'desc':'Total Vaccines',
            'field':'data.vaccinations.CUMMULATIVE_DAILY_DOSES_ADMINISTERED',
            'date_check': 'data.vaccinations.DATE',
            'params':(15979099, 64075795, 0, 486334.0,	0, 0.011909),
            'flags':('always_changes','never_sinks')
        },
        {   'desc':'Total Cases',
            'field':'data.cases.LATEST_TOTAL_CONFIRMED_CASES',
            'date_check': 'data.cases.DATE',
            'params':(3553307.0, 5428522.0,  -4359.0, 237084.0,   -0.001173, 0.045668),
            'flags':('always_changes')
        },
        {   'desc':'Cases per 100k',
            'field':'data.cases.LATEST_CONFIDENT_AVG_CASE_RATE_PER_100K_7_DAYS',
            'date_check': 'data.cases.DATE',
            'params':(1.7, 70.6,  -2.6, 24.6,   -0.275248, 0.537498),
            'flags':()
        },
        {   'desc':'Total Deaths',
            'field':'data.deaths.LATEST_TOTAL_CONFIRMED_DEATHS',
            'date_check': 'data.deaths.DATE',
            'params':(57091.0, 75924.0,  -352.0, 4214.0,   -0.005472, 0.073812),
            'flags':()
        },
        {   'desc':'Deaths per 100k',
            'field':'data.deaths.LATEST_CONFIDENT_AVG_DEATH_RATE_PER_100K_7_DAYS',
            'date_check': 'data.deaths.DATE',
            'params':(0.01851, 0.25097,  -0.01958, 0.02670,   -0.12003, 0.78948),
            'flags':()
        },
        {   'desc':'Test Positivity Rate',
            'field':'data.tests.LATEST_CONFIDENT_POSITIVITY_RATE_7_DAYS',
            'date_check': 'data.tests.DATE',
            'params':(0.00700, 0.20379,  -0.00941, 0.04473,   -0.43868, 0.79013),
            'flags':('always_changes')
        },
    ]
  },
  {
    'filename': 'data/dashboard/vaccines/sparkline.json',
    'branch': 'CovidStateDashboardVaccines_Sparkline_Staging',
    'pdate_field': 'meta.PUBLISHED_DATE',
    'fields_of_interest': [
        {   'desc':'Vaccines Daily Avg',
            'field':'data.population.DAILY_AVERAGE',
            'params':(68841, 222837, -29920, 37064, -0.157256, 0.256153),
            'flags':('always_changes')
        },
        {   'desc':'Pct Population Vaxed',
            'field':'data.population.TOTAL_VAXED_RATIO',
            'params': (0.73717, 0.81433,-0.07716, 0.00186, -0.09476,0.00252),
            'flags':('always_changes')
        },
    ]
  },
  {
    'filename': 'data/dashboard/confirmed-cases/california.json',
    'branch': 'CovidStateDashboardTables_Staging',
    'pdate_field': 'meta.PUBLISHED_DATE',
    'fields_of_interest': [
        {   'desc':'Cases Daily Avg',
            'field':'data.latest.CONFIRMED_CASES.CASES_DAILY_AVERAGE',
            'params':(3654.3, 10280.4, -1063.6, 2509.4, -0.115185, 0.40631),
            'flags':('always_changes')
        },
    ]
  },
  {
    'filename': 'data/dashboard/confirmed-deaths/california.json',
    'branch': 'CovidStateDashboardTables_Staging',
    'pdate_field': 'meta.PUBLISHED_DATE',
    'fields_of_interest': [
        {   'desc':'Deaths Daily Avg',
            'field':'data.latest.CONFIRMED_DEATHS.DEATHS_DAILY_AVERAGE',
            'params':(42, 102.7,  -10, 5,   -0.125616, 0.102941),
            'flags':('always_changes')
        },
    ]
  },
]

# # deaths daily average: TRIGGER SINK: old: 45.285714 new: 40.857143 delta: -4.428571 growth: -0.097792 min_change -0.01950, min_growth: -0.12003
