# cagov_config
min_sleep = 0
max_sleep = 1
min_chartcheck_sleep = 300
max_chartcheck_sleep = 301

# root_url = 'http://localhost:8000'
root_url = 'https://covid19.ca.gov'

drought_wp_url_posts = 'https://live-drought-ca-gov.pantheonsite.io/wp-json/wp/v2/posts?order=desc'
drought_wp_url_pages = 'https://live-drought-ca-gov.pantheonsite.io/wp-json/wp/v2/pages?order=desc'

removals = [
    r'<p class="small-text">Last upd.*?</p>'
]

replacements = [
    (r'wp-container-[0-9a-f]+','wp-container')
]


holidays = ['2022-02-21', # presidents day
            '2022-03-31', # cesar chavez day
            '2022-05-30', # memorial day
            '2022-07-04', # independence day
            '2022-09-05', # labor day
            '2022-11-11', # veterens day
            '2022-11-24', # thanksgiving
            '2022-11-25', # day after thanksgiving
            '2022-12-25', # christmas
            ]

'''
to eliminate


<p class="small-text">Last updated&nbsp;January 5, 2021 at 10:26 AM</p>



'''
