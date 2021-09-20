# chart checker
#
# -*- coding: utf-8 -*-
#
import re, sys, os, time, argparse, random, importlib
from datetime import datetime, date
import http.client, urllib
import requests, json
from types import SimpleNamespace


# reopen stdout as utf-8, to avoid encoding errors on console messages
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

parser = argparse.ArgumentParser(description='Clicky Stats Daemon')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose')
parser.add_argument('-t', '--test', default=False, action='store_true', help='Test - broadcast to testingbot only')
parser.add_argument('-q', '--quiet', default=False, action='store_true', help='No broadcasting')
parser.add_argument('-config', default="cagov_config", help='Config file name prefix, default=%(default)s')
args = parser.parse_args()

cagov_config = importlib.import_module(args.config)
from slack_credentials import slackbot_token
from slack_info import slackAlertChannel, slackStateDashChannel, slackOutagesChannel, slackBotDebugChannel

def post_message_to_slack(text, blocks = None, channel=slackAlertChannel):
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slackbot_token,
        'channel': channel,
        'text': text,
        # 'icon_url': slack_icon_url,
        # 'username': slack_user_name,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()


# get today's date
#
NBR_TEST_BITS = 12
IDX_DATE_SUMMARY = 0
IDX_DATE_CASES = 1
IDX_MATCH_CASES = 2
IDX_DATE_DEATHS = 3
IDX_MATCH_DEATHS = 4
IDX_DATE_TESTS = 5
IDX_MATCH_TESTS = 6  # no longer used
IDX_DATE_GROUPS = 7
IDX_DATE_POSITIVITY = 8
IDX_DATE_PATIENTS = 9
IDX_DATE_ICUBEDS = 10
IDX_SPARKLINES = 11

def do_tests():
    total_tests = 0
    total_passes = 0
    passes = [0] * NBR_TEST_BITS
    msgs = []
    now = date.today()
    now_datestr = now.strftime('%B %-d, %Y')
    now_snowdate = now.strftime('%Y-%m-%d')
    r = requests.get('https://covid19.ca.gov/state-dashboard')
    text = r.text.replace("\n"," ")

    def fetch_str(pattern, text):
        m = re.search(pattern,text)
        if m:
            return m.group(1)
        print("! not found")
        return ""

    site_datestr = fetch_str(r'<p class="small-text">Last updated\&nbsp;(.*?) at',text)
    # check if report date is today
    total_tests += 1
    if site_datestr == now_datestr:
        passes[IDX_DATE_SUMMARY] = 1
        total_passes += 1
        msgs.append("Site has today's summary data")
    else:
        msgs.append("Site was updated in the past")

    # fetch summary boxes
    try:
        site_cases_total = int(fetch_str(r'<div id="total-cases-number" .*?<strong>(.*?)</strong',text).replace(',',''))
        site_deaths_total = int(fetch_str(r'<div id="total-deaths-number" .*?<strong>(.*?)</strong',text).replace(',',''))
        # site_tests_total = int(fetch_str(r'<div id="total-tested-number" .*?<strong>(.*?)</strong',text).replace(',',''))
        # if fetch_str(r'<div id="total-cases-today" .*?<strong>(.*?)</strong',text).replace(',','').isnumeric():
        #     site_cases_today = int(fetch_str(r'<div id="total-cases-today" .*?<strong>(.*?)</strong',text).replace(',',''))
        #     site_deaths_today = int(fetch_str(r'<div id="total-deaths-today" .*?<strong>(.*?)</strong',text).replace(',',''))
        #     # site_tests_today = int(fetch_str(r'<div id="total-tested-today" .*?<strong>(.*?)</strong',text).replace(',',''))
        # else:
        #     if args.verbose:
        #         print("Got hyphens",fetch_str(r'<div id="total-cases-today" .*?<strong>(.*?)</strong',text))
        #     site_cases_today = -1
        #     site_deaths_today = -1
        site_cases_today = -1
        site_deaths_today = -1
        site_tests_today = -1
    except Exception as e:
        if args.verbose:
            print ("!! parse error")
            print(e)
        msgs.append("Parse error")
        return ([], msgs)

    # fetch json for graphs
    cases_file_url = 'https://files.covid19.ca.gov/data/dashboard/confirmed-cases/california.json?x=x'
    deaths_file_url = 'https://files.covid19.ca.gov/data/dashboard/confirmed-deaths/california.json?x=x'
    tests_file_url = 'https://files.covid19.ca.gov/data/dashboard/total-tests/california.json?x=x'
    positivity_file_url = 'https://files.covid19.ca.gov/data/dashboard/positivity-rate/california.json?x=x'
    patients_file_url = 'https://files.covid19.ca.gov/data/dashboard/patients/california.json?x=x'
    icubeds_file_url = 'https://files.covid19.ca.gov/data/dashboard/icu-beds/california.json?x=x'
    groups_file_url = 'https://files.covid19.ca.gov/data/infections-by-group/infections-by-group-california.json'
    sparklines_cases_url = 'https://files.covid19.ca.gov/img/generated/sparklines/sparkline-cases.svg'



    r = requests.get(cases_file_url)
    case_data = json.loads(r.text, object_hook=lambda d: SimpleNamespace(**d))
    case_snowdate = case_data.meta.PUBLISHED_DATE
    chart_cases_total = case_data.data.latest.CONFIRMED_CASES.total_confirmed_cases
    chart_cases_today = case_data.data.latest.CONFIRMED_CASES.new_cases

    total_tests += 1
    if case_snowdate == now_snowdate:
        passes[IDX_DATE_CASES] = 1
        total_passes += 1
        msgs.append("Site has today's case chart data")
    else:
        msgs.append("Case chart data is stale")

    total_tests += 1
    if chart_cases_total == site_cases_total and (site_cases_today == -1 or chart_cases_today == site_cases_today):
        passes[IDX_MATCH_CASES] = 1
        total_passes += 1
    else:
        msgs.append("Cases in charts (%d/%d) mismatch summaries (%d/%d)" %(chart_cases_total,chart_cases_today,site_cases_total,site_cases_today))

    r = requests.get(deaths_file_url)
    death_data = json.loads(r.text, object_hook=lambda d: SimpleNamespace(**d))
    death_snowdate = death_data.meta.PUBLISHED_DATE
    chart_deaths_total = death_data.data.latest.CONFIRMED_DEATHS.total_confirmed_deaths
    chart_deaths_today = death_data.data.latest.CONFIRMED_DEATHS.new_deaths

    total_tests += 1
    if death_snowdate == now_snowdate:
        passes[IDX_DATE_DEATHS] = 1
        total_passes += 1
        msgs.append("Site has today's deaths chart data")
    else:
        msgs.append("Death chart data is stale")

    total_tests += 1
    if chart_deaths_total == site_deaths_total and (site_deaths_today == -1 or chart_deaths_today == site_deaths_today):
        passes[IDX_MATCH_DEATHS] = 1
        total_passes += 1
    else:
        msgs.append("Deaths in charts (%d/%d) mismatch summaries (%d/%d)" % (chart_deaths_total,chart_deaths_today,site_deaths_total,site_deaths_today))

    r = requests.get(tests_file_url)
    test_data = json.loads(r.text, object_hook=lambda d: SimpleNamespace(**d))
    test_snowdate = test_data.meta.PUBLISHED_DATE
    chart_tests_total = test_data.data.latest.TOTAL_TESTS.total_tests_performed
    chart_tests_today = test_data.data.latest.TOTAL_TESTS.new_tests_reported

    total_tests += 1
    if test_snowdate == now_snowdate:
        passes[IDX_DATE_TESTS] = 1
        total_passes += 1
        msgs.append("Site has today's tests chart data")
    else:
        msgs.append("Test chart data is stale")

    # total_tests += 1
    # if chart_tests_total == site_tests_total and (site_tests_today == -1 or chart_tests_today == site_tests_today):
    #     passes[IDX_MATCH_TESTS] = 1
    #     total_passes += 1
    # else:
    #      msgs.append("Tests in charts (%d/%d) mismatch summaries (%d/%d)" % (chart_tests_total,chart_tests_today,site_tests_total,site_tests_today))
    passes[IDX_MATCH_TESTS] = passes[IDX_MATCH_CASES] # force match/unmatch for this

    r = requests.get(groups_file_url)
    group_data = json.loads(r.text, object_hook=lambda d: SimpleNamespace(**d))
    group_snowdate = group_data.meta.PUBLISHED_DATE
    total_tests += 1
    if group_snowdate == now_snowdate:
        passes[IDX_DATE_GROUPS] = 1
        total_passes += 1
        msgs.append("Site has today's groups chart data")
    else:
        msgs.append("Groups chart data is stale")

    r = requests.get(positivity_file_url)
    group_data = json.loads(r.text, object_hook=lambda d: SimpleNamespace(**d))
    group_snowdate = group_data.meta.PUBLISHED_DATE
    total_tests += 1
    if group_snowdate == now_snowdate:
        passes[IDX_DATE_POSITIVITY] = 1
        total_passes += 1
        msgs.append("Site has today's positivity chart data")
    else:
        msgs.append("Positivity chart data is stale")

    r = requests.get(patients_file_url)
    group_data = json.loads(r.text, object_hook=lambda d: SimpleNamespace(**d))
    group_snowdate = group_data.meta.PUBLISHED_DATE
    total_tests += 1
    if group_snowdate == now_snowdate:
        passes[IDX_DATE_PATIENTS] = 1
        total_passes += 1
        msgs.append("Site has today's patient chart data")
    else:
        msgs.append("Patient chart data is stale")

    r = requests.get(icubeds_file_url)
    group_data = json.loads(r.text, object_hook=lambda d: SimpleNamespace(**d))
    group_snowdate = group_data.meta.PUBLISHED_DATE
    total_tests += 1
    if group_snowdate == now_snowdate:
        passes[IDX_DATE_ICUBEDS] = 1
        total_passes += 1
        msgs.append("Site has today's ICU-bed chart data")
    else:
        msgs.append("ICU-bed chart data is stale")

    r = requests.get(sparklines_cases_url)
    text = r.text.replace("\n"," ")
    publish_date = fetch_str(r'DATA_PUBLISHED_DATE:(.*?),',text)
    total_tests += 1
    if publish_date == now_snowdate:
        passes[IDX_SPARKLINES] = 1
        total_passes += 1
        msgs.append("Site has today's cases sparkline")
    else:
        msgs.append("Cases sparkline is stale")


    msgs.append("%d/%d tests pass" % (total_passes, total_tests))
    return passes, msgs

# report if numbers match/differ
#
# look at summary box data in main branch
# look at chart data in main branch
# check if those numbers are in alignment
# check if those numbers match what is on website
# check if dates on those numbers are current
#
# look for PRs, if any, and check those numbers
# flag masks
FM_ALL_DONE = 0xFFF  # all tests passed
FM_ALL_STALE = 0x54 # only the content tests pass
FM_DATE_TESTS = 0xFAB # chart date tests
FM_CONTENT_TESTS = 0x54  # chart content match tests

last_res_mask = FM_ALL_DONE
runs = 0

try:
    while True:
        sys.stdout.flush()
        if runs > 0:
            # random sleep
            now = datetime.now()
            if now.hour == 9 and last_res_mask != FM_ALL_DONE:
                sleep_secs = 30
            elif last_res_mask == FM_ALL_DONE:
                # sleep til midnight
                sleep_secs = (23-now.hour)*60*60 + (59-now.minute)*60 + 60-now.second
            elif last_res_mask == FM_ALL_STALE and now.hour < 9:
                # sleep til 9am
                sleep_secs = (8-now.hour)*60*60 + (59-now.minute)*60 + 60-now.second
            else:
                sleep_secs = 300
            if args.verbose:
                print("Sleeping",sleep_secs)
            time.sleep(sleep_secs)
        importlib.reload(cagov_config)
        try:
            res, msgs = do_tests()
            runs += 1
        except Exception as e:
            print("Error running tests",e)
            sys.exit(0)

        if len(res) == 0: # parse error
            print("Parse Error")
            continue
            
        # testing
        # res = [1,1,0,1,1,1,1,1,1,1,1]
        # last_res_mask = FM_ALL_STALE

        flag_mask = 0
        for i in range(len(res)):
            if res[i]:
                flag_mask |= (1 << i)
        if args.verbose:
            print("Got Status %02x" % (flag_mask))
        if flag_mask != last_res_mask:
            print("STATUS CHANGE %s %02x" % ( datetime.now().strftime('%B %-d, %Y %H:%M:%S'), flag_mask ), res)
            print(msgs)
            broadcast_msg = ''
            chartdatebits = {'summaries':0,'cases-charts':1,'deaths-charts':3,'testing-charts':5,'groups-charts':7,'positivity-chart':8,'patients-charts':9,'ICU-beds-chart':10,'Sparklines':11}
            chartmatchbits = {'cases':2,'deaths':4,'tests':6}
            big_broadcast = False
            if flag_mask == FM_ALL_DONE:
                broadcast_msg = '/state-dashboard/ has been fully updated (charts match summaries, sparklines updated)'
                big_broadcast = True
            elif flag_mask == FM_ALL_STALE:
                pass
            elif (flag_mask & FM_DATE_TESTS) == FM_DATE_TESTS and (flag_mask & FM_CONTENT_TESTS) != FM_CONTENT_TESTS:
                missmatched_items = [nom for nom,idx in chartmatchbits.items() if res[idx] == 0]
                broadcast_msg = '/state-dashboard/ has been fully updated, but %s charts don\'t match summaries' % ('/'.join(missmatched_items))
                big_broadcast = False
            else:
                updated_items_prev = [nom for nom,idx in chartdatebits.items() if (last_res_mask & (1 << idx))]
                updated_items_new = [nom for nom,idx in chartdatebits.items() if (flag_mask & (1 << idx))]
                new_items = list(set(updated_items_new).difference(set(updated_items_prev)))
                if last_res_mask == FM_ALL_STALE:
                    broadcast_msg = '/state-dashboard/ updates are starting (%s added)' % (','.join(new_items))
                    big_broadcast = True
                else:
                    broadcast_msg = '/state-dashboard/ has been partially updated (%s added)' % (','.join(new_items))
            if broadcast_msg != '':
                print("BROADCAST MESSAGE: %s" % (broadcast_msg))
                if not args.quiet:
                    if args.test:
                        post_message_to_slack(broadcast_msg, channel=slackBotDebugChannel)
                    else:
                        if big_broadcast:
                            post_message_to_slack(broadcast_msg, channel=slackStateDashChannel)
                        post_message_to_slack(broadcast_msg, channel=slackAlertChannel)
                    
            # post meaningful message to slack here...
        else:
            if args.verbose:
                print("No Change: res %02x" %(flag_mask))
        last_res_mask = flag_mask
except KeyboardInterrupt:
    print('interrupted!')

time.sleep(1)        

'''
STATUS CHANGE May 1, 2021 22:24:07 [1, 1, 1, 1, 1, 1, 1]
["Site has today's summary data", "Site has today's case chart data", "Site has today's deaths chart data", "Site has today's tests chart data", '7/7 tests pass']
Normal
7

STATUS CHANGE May 2, 2021 00:04:23 [0, 0, 1, 0, 1, 0, 1]
['Site was updated yesterday', 'Case chart data is from yesterday', "Death chart data has yesterday's date", 'Test chart data is stale', '3/7 tests pass']
[0, 0, 1, 0, 1, 0, 1]
Normal midmight-9am reading

STATUS CHANGE May 2, 2021 09:10:38 [0, 1, 0, 1, 0, 0, 1]
['Site was updated yesterday', "Site has today's case chart data", 'Cases in charts (3642480/2254) mismatch summaries (3640226/2094)', "Site has today's deaths chart data", 'Deaths in charts (60748/123) mismatch summaries (60625/158)', 'Test chart data is stale', '3/7 tests pass']
Normal site updating from 9-9:30am
[0, 1, 0, x, x, 0, 1] or 
[0, 1, 0, 0, 1, x, x] 
"Chart data is being updated" (Use this for any incomplete set of matching dates for charts with no summary)
Add a note if the current time is odd - this is expected between 9-9:30

STATUS CHANGE May 2, 2021 09:20:40 [0, 1, 0, 1, 0, 1, 0]
['Site was updated yesterday', "Site has today's case chart data", 'Cases in charts (3642480/2254) mismatch summaries (3640226/2094)', "Site has today's deaths chart data", 'Deaths in charts (60748/123) mismatch summaries (60625/158)', "Site has today's tests chart data", 'Tests in charts (60514937/249137) mismatch summaries (60265800/249872)', '3/7 tests pass']
Normal site updating from 9-9:30am
[0, 1, 0, 1, 0, 1, 0]
"Chart data has been updated, awaiting summary boxes."
Add a note if the current time is odd - this is expected between 9-9:30

STATUS CHANGE May 2, 2021 09:25:41 [1, 1, 1, 1, 1, 1, 1]
["Site has today's summary data", "Site has today's case chart data", "Site has today's deaths chart data", "Site has today's tests chart data", '7/7 tests pass']
Summary boxes have been updated, charts match.
Add a note if this does not first occur between 9:15-9:45am

Things that should never happen (special alerts)
Summary box is up to date, and chart data is not (chart data generally precedes summary box)
[1, 0, x, 0, x, 0, x]
Summary box dates match chart dates (both today or yesterday), but chart data mismatches summaries.
[1, 0, x, 0, x, 0, x]
Late updates - note it.

Features to add: 
* Increase polling frequency to 1m between 9 and 9:30 until fully updated.
* Check status of bottom chart (use JSON)

Messages to produce:
/state-dashboard/ has been parially updated (cases/deaths/testing/group charts)
(produce one for each partial update change)
/state-dashboard/ has been fully updated


'''