# demandbot_config.py
trigger_factor = 2.0
deltabase_name = 'deltabase.json'
# holidays = ['2022-01-03']
busy_sleep = 60*5
offhours_sleep = 60*60
# param order is:
# min_value, max_value, min_change, max_change, min_growth, max_growth

# xian https://cadotgov.slack.com/team/U01KHGNK8KU
# aaron https://cadotgov.slack.com/team/UQTUFH6FL
# jbum https://cadotgov.slack.com/team/U01ELJEJ1SM
# james logan : U03G2SJ2PEY
who_to_notify = '<@U01ELJEJ1SM> <@U03G2SJ2PEY>'

file_list = [
  {
    'filename': 'data/daily-stats-v2.json',
    'branch': 'CovidStateDashboard_Summary_Staging',
    'pdate_field': 'meta.PUBLISHED_DATE',
    'fields_of_interest': [
        # {   'desc':'Total Vaccines',
        #     'field':'data.vaccinations.CUMMULATIVE_DAILY_DOSES_ADMINISTERED',
        #     'date_check': 'data.vaccinations.DATE',
        #     'expected_growth_range': (0.000000, 0.011909),
        #     # (15979099.0, 65841193.0,  0.0, 401877.0,   0.000000, 0.011909),
        #     'flags':('always_changes','never_sinks')
        # },
        {   'desc':'Total Cases',
            'field':'data.cases.LATEST_TOTAL_CONFIRMED_CASES',
            'date_check': 'data.cases.DATE',
            'expected_growth_range': (-0.001173, 0.018733),
            # (3553307.0, 5634357.0,  -4359.0, 103606.0,   -0.001173, 0.018733),
            'flags':('always_changes')
        },
        {   'desc':'Cases per 100k',
            'field':'data.cases.LATEST_CONFIDENT_AVG_CASE_RATE_PER_100K_7_DAYS',
            'date_check': 'data.cases.DATE',
            'expected_growth_range': (-0.136690, 0.257196),
            # (1.7, 124.5,  -2.6, 18.3,   -0.136690, 0.257196),
            'flags':()
        },
        {   'desc':'Total Deaths',
            'field':'data.deaths.LATEST_TOTAL_CONFIRMED_DEATHS',
            'date_check': 'data.deaths.DATE',
            'expected_growth_range': (-0.005472, 0.003840),
            # 'params':(57091.0, 76341.0,  -352.0, 292.0,   -0.005472, 0.003840),
            'flags':()
        },
        {   'desc':'Deaths per 100k',
            'field':'data.deaths.LATEST_CONFIDENT_AVG_DEATH_RATE_PER_100K_7_DAYS',
            'date_check': 'data.deaths.DATE',
            'expected_growth_range': (-0.11767, 0.25000),
            # 'params':(0.01851, 0.25097,  -0.01495, 0.01780,   -0.11767, 0.25000),
            'flags':()
        },
        {   'desc':'Total Tests',
            'field':'data.tests.LATEST_TOTAL_TESTS_PERFORMED',
            'date_check': 'data.tests.DATE',
            'expected_growth_range': (0.000000, 0.009421),
            # (52765254.0, 122721928.0,  0.0, 816603.0,   0.000000, 0.009421),
            'flags':('always_changes')
        },
        {   'desc':'Newly Reported Tests',
            'field':'data.tests.NEWLY_REPORTED_TESTS',
            'date_check': 'data.tests.DATE',
            'expected_growth_range': (-0.909324, 0.968579),
            # (45230.0, 1498225.0,  -1285662.0, 411048.7,   -0.909324, 0.968579),
            'flags':('always_changes')
        },
        {   'desc':'Test Positivity Rate',
            'field':'data.tests.LATEST_CONFIDENT_POSITIVITY_RATE_7_DAYS',
            'date_check': 'data.tests.DATE',
            'expected_growth_range': (-0.21198, 0.27496),
            # (0.00700, 0.21746,  -0.00941, 0.02998,   -0.21198, 0.27496),
            'flags':('always_changes')
        },
        {   'desc':'Total Hospitalizations',
            'field':'data.hospitalizations.HOSPITALIZED_COVID_CONFIRMED_PATIENTS',
            'date_check': 'data.hospitalizations.DATE',
            'expected_growth_range': (-0.048780, 0.114062),
            # (915.0, 9279.0,  -306.0, 639.0,   -0.048780, 0.114062),
            'flags':('always_changes')
        },
        {   'desc':'Total ICU',
            'field':'data.icu.ICU_COVID_CONFIRMED_PATIENTS',
            'date_check': 'data.icu.DATE',
            'expected_growth_range': (-0.093923, 0.181070),
            # (219.0, 2128.0,  -143.0, 192.0,   -0.093923, 0.181070),
            'flags':('always_changes')
        },
        # Hospitalization Changee and ICU change is sometimes zero which produces issues
    ]
  },
  {
    'filename': 'data/dashboard/vaccines/sparkline.json',
    'branch': 'CovidStateDashboardVaccines_Sparkline_Staging',
    'pdate_field': 'meta.PUBLISHED_DATE',
    'fields_of_interest': [
        {   'desc':'Vaccines Daily Avg',
            'field':'data.population.DAILY_AVERAGE',
            'date_check': 'data.time_series.VACCINE_DOSES.DATE_RANGE.MAXIMUM',
            'expected_growth_range': (-0.157256, 0.256153),
            # (68841.0, 222837.0,  -29920.0, 37064.0,   -0.157256, 0.256153),
            'flags':('always_changes')
        },
        {   'desc':'Pct Population Vaxed',
            'field':'data.population.TOTAL_VAXED_RATIO',
            'date_check': 'data.time_series.VACCINE_DOSES.DATE_RANGE.MAXIMUM',
            'expected_growth_range': (-0.09476, 0.00252),
            # (0.73717, 0.81433,  -0.07716, 0.00186,   -0.09476, 0.00252),
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
            'date_check': 'data.time_series.CONFIRMED_CASES_EPISODE_DATE.DATE_RANGE.MAXIMUM',
            'expected_growth_range': (-0.115185, 0.264286),
            # (3654.3, 43697.4,  -1063.6, 7584.3,   -0.115185, 0.264286),
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
            'date_check': 'data.time_series.CONFIRMED_DEATHS_DEATH_DATE.DATE_RANGE.MAXIMUM',
            'expected_growth_range': (-0.097778, 0.094406),
            # (40.9, 102.7,  -6.3, 4.4,   -0.097778, 0.094406),
            'flags':('always_changes')
        },
    ]
  },
#   {
#     'filename': 'data/dashboard/postvax/california.json',
#     'branch': 'CovidStateDashboardPostvax_Staging',
#     'pdate_field': 'meta.PUBLISHED_DATE',
#     'expected_changed_date_field': 'meta.REPORT_DATE',
#     'fields_of_interest': [
#         {   'desc':'Unvax Case Rate',
#             'date_check': 'data[-1].DATE',
#             'field':'data[-1].UNVAX_CASE_RATE',
#             'expected_growth_range': (-0.386463, 0.115673),
#             # (19.4, 300.7,  -18.0, 26.2,   -0.386463, 0.115673),
#             'flags':('always_changes')
#         },
#         {   'desc':'Vax Case Rate',
#             'date_check': 'data[-1].DATE',
#             'field':'data[-1].VAX_CASE_RATE',
#             'expected_growth_range': (-0.128, 0.062),
#             'flags':('always_changes')
#         },
#         {   'desc':'Boost Case Rate',
#             'date_check': 'data[-1].DATE',
#             'field':'data[-1].BOOST_CASE_RATE',
#             'expected_growth_range': (-0.083, 0.042),
#             'flags':('always_changes')
#         },
#     ]
#   },
]
