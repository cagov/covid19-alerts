# chart checker v2
#
# -*- coding: utf-8 -*-
#
# This checks for various updates to the COVID-19 state-dashboard page and reports the morning updates 
# (and possible issues) to Slack via the #covid19-alerts and #covid19-state-dashboard channels.
# 
#
# see if there is a way to pull numbers from tableau charts.

import re, sys, time, argparse, importlib
from datetime import datetime, timedelta
from pytz import timezone
import requests, json
from xml.dom.minidom import parseString

# from chart_checker_tests import chart_tests
from jbum_pushover import pushover_app_token, pushover_user_key

# reopen stdout as utf-8, to avoid encoding errors on console messages
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

parser = argparse.ArgumentParser(description='chart checker v2')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose')
parser.add_argument('-t', '--test', default=False, action='store_true', help='Test - broadcast to testingbot only')
parser.add_argument('-q', '--quiet', default=False, action='store_true', help='No broadcasting')
parser.add_argument('-config', default="cagov_config", help='Config file name prefix, default=%(default)s')
args = parser.parse_args()

cagov_config = importlib.import_module(args.config)
chart_checker_tests = importlib.import_module('chart_checker_tests')
chart_tests = chart_checker_tests.chart_tests
from slack_credentials import slackbot_token
from slack_info import slackAlertChannel, slackStateDashChannel, slackJimDebugChannel

def post_message_to_slack(text, blocks = None, channel=slackAlertChannel):
    if not args.quiet:
        requests.post('https://slack.com/api/chat.postMessage', {
            'token': slackbot_token,
            'channel': channel,
            'text': text,
            'icon_emoji': ':pipe:',
            # 'icon_url': slack_icon_url,
            # 'username': slack_user_name,
            'blocks': json.dumps(blocks) if blocks else None
        }).json()

def send_pushover(message, title='CAGOVAlert', url=None, url_title=None):
    global args
    try:
        print("Broadcasting message:",message)
        if args.test:
            return
        payload = {"token": pushover_app_token, 
                "user": pushover_user_key, 
                "title": title,
                "message": message} 
        if url is not None:
            payload['url'] = url
            payload['url_title'] = url_title

        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode(payload), 
            { "Content-type": "application/x-www-form-urlencoded" })
        r = conn.getresponse()
        if r.status != 200:
            raise httplib.HTTPException("Response not 200")
    except Exception as e:
        print(e)
        pass

# get today's date
#

def do_tests():
    total_tests = 0
    total_passes = 0
    passes = [0] * len(chart_tests)
    msgs = []
    now = datetime.today()
    now_datestr = now.strftime('%B %-d, %Y')
    now_snowdate = now.strftime('%Y-%m-%d')

    cache_requests = {}

    def fetch_str(pattern, text):
        m = re.search(pattern,text)
        if m:
            return m.group(1)
        print("! not found")
        return ""

    def fetch_url(url):
        if url not in cache_requests:
            cache_requests[url] = requests.get(url)
        return cache_requests[url]

    def fetch_json_field(data, fieldstr):
        for token in fieldstr.split('.'):
            if token in data:
                data = data[token]
            else:
                return None
        return data

    exception_occured = False
    for ti,trec in enumerate(chart_tests):
        is_pass = False
        # if args.verbose:
        #     print("TREC %s" % (trec['nom']))

        try:
            if trec['test_type'] == 'PASS':
                # pass
                is_pass = True
            elif trec['test_type'] == 'DATE_MATCHES_TODAY':
                if 'json_url' in trec:
                    jr = fetch_url(trec['json_url'])
                    data = json.loads(jr.text)
                    datestr = fetch_json_field(data, trec['json_field'])
                    is_pass = datestr == now_snowdate
                elif 'svg_url' in trec:
                    jr = fetch_url(trec['svg_url'])
                    datestr = json.loads(parseString(jr.text).documentElement.getAttribute('meta'))[trec['meta_field']]
                    is_pass = datestr == now_snowdate
                else:
                    r = fetch_url(trec['url'])
                    datestr = fetch_str(trec['pat'], r.text.replace("\n"," "))
                    is_pass = datestr == now_datestr
            elif trec['test_type'] == 'DATE_WEEKLY_MATCH':
                from datetime import date as dtdate
                from datetime import time as dttime
                last_matchday = datetime.combine(dtdate.today(),dttime())  # today at midnight
                while last_matchday.weekday() != trec['weekday']:
                    last_matchday -= timedelta(days=1)
                if 'json_url' in trec:
                    jr = fetch_url(trec['json_url'])
                    data = json.loads(jr.text)
                    datestr = fetch_json_field(data, trec['json_field'])
                else:
                    r = fetch_url(trec['url'])
                    datestr = fetch_str(trec['pat'], r.text.replace("\n"," "))
                is_pass = datetime.strptime(datestr,'%Y-%m-%d') >= last_matchday
            elif trec['test_type'] == 'NUMBER_MATCHES_JSON':
                r = fetch_url(trec['url'])
                numsrc = int(fetch_str(trec['pat'], r.text.replace("\n"," ")).replace(',',''))
                jr = fetch_url(trec['json_url'])
                data = json.loads(jr.text)
                numtgt = fetch_json_field(data, trec['json_field'])
                is_pass = numsrc == numtgt
            else:
                print("Invalid Test Type",trec['test_type'])
        except Exception as e:
            is_pass = False
            exception_occured = True
            print ("!! exception on ",trec)
            print(e)
            msgs.append("%s !! exception" % (trec['nom']))
            continue

        total_tests += 1
        if is_pass:
            passes[ti] = 1
            total_passes += 1
            msgs.append("%s PASS" % (trec['nom']))
        else:
            msgs.append("%s FAIL" % (trec['nom']))

    msgs.append("%d/%d tests pass" % (total_passes, total_tests))
    return passes, msgs, exception_occured

# EXPECTED_STALE_PASSES - tests expected to PASS after midnight
# FM_ALL_DONE - tests expected to PASS after 9:30
# FM_DATE_TESTS - DATE tests expected to PASS after 9:30
# FM_CONTENT_TESTS - content tests expected to fail around 9:20, but pass at 9:30

def compute_expected_passes():
    curDay = datetime.now().weekday()
    now_snowdate = datetime.today().strftime('%Y-%m-%d')
    isHoliday = now_snowdate in cagov_config.holidays

    FM_DATE_TESTS = 0 # dates expected to pass post 9am
    FM_CONTENT_TESTS = 0 # content tests expected to pass (normally, all of them, all the time)
    FM_EXPECTED_STALE_PASSES = 0 # tests expected to pass from midnight to 9:30am

    for i,trec in enumerate(chart_tests):
        active_days = trec['active_days'] if 'active_days' in trec else chart_checker_tests.all_days

        if 'DATE' in trec['test_type']:
            stale_days = trec['stale_days'] if 'stale_days' in trec else chart_checker_tests.all_days
            if active_days[curDay] and not (isHoliday and 'not-on-holidays' in trec):
                FM_DATE_TESTS |= (1 << i)
            if not stale_days[curDay]: # only one that gets this is a wednesday only test...
                FM_EXPECTED_STALE_PASSES |= (1 << i)
        else:
            # content tests should always pass
            FM_CONTENT_TESTS |= (1 << i) # content expected to pass
            FM_EXPECTED_STALE_PASSES |= (1 << i)

    FM_ALL_DONE = FM_DATE_TESTS | FM_CONTENT_TESTS
    return (FM_DATE_TESTS, FM_CONTENT_TESTS, FM_ALL_DONE, FM_EXPECTED_STALE_PASSES)


FM_DATE_TESTS, FM_CONTENT_TESTS, FM_ALL_DONE, FM_EXPECTED_STALE_PASSES = compute_expected_passes()
last_res_mask = FM_ALL_DONE
runs = 0
stale_alert_issued = False

try:
    while True:
        sys.stdout.flush()
        if runs > 0:
            # random sleep
            now = datetime.now().astimezone(timezone('US/Pacific'))

            if (now.hour == 9 or now.hour == 10) and last_res_mask != FM_ALL_DONE:
                sleep_secs = 30
            elif last_res_mask == FM_ALL_DONE:
                # sleep til midnight
                sleep_secs = (23-now.hour)*60*60 + (59-now.minute)*60 + 60-now.second
            elif last_res_mask == FM_EXPECTED_STALE_PASSES and now.hour < 9:
                # sleep til next hour
                # previously we slept til 9, but this broke on daylight savings days
                # sleep_secs = (8-now.hour)*60*60 + (59-now.minute)*60 + 60-now.second
                sleep_secs = (59-now.minute)*60 + 60-now.second
            else:
                sleep_secs = 300
            if args.verbose:
                print("Sleeping",sleep_secs)
            time.sleep(sleep_secs)

        importlib.reload(cagov_config)
        importlib.reload(chart_checker_tests)
        # recompute masks upon waking up and reloading tests
        FM_DATE_TESTS, FM_CONTENT_TESTS, FM_ALL_DONE, FM_EXPECTED_STALE_PASSES = compute_expected_passes()
        chart_tests = chart_checker_tests.chart_tests
        try:
            res, msgs, exception_occured = do_tests()
            runs += 1
        except Exception as e:
            print("Error running tests",e)
            sys.exit(0)
        if len(res) == 0: # parse error
            print("Parse Error")
            continue
        if exception_occured:
            print("Ignoring exception")
            post_message_to_slack("Chart Checker raised an exception", channel=slackJimDebugChannel)
            continue
            
        # recompute expected staleness mask here...
        # FM_EXPECTED_STALE_PASSES = compute_staleness_mask()

        flag_mask = 0
        for i in range(len(res)):
            if res[i]:
                flag_mask |= (1 << i)
        if args.verbose:
            print("Got Status %02x" % (flag_mask))

        if flag_mask != last_res_mask:
            print("STATUS CHANGE %s %02x" % ( datetime.now().strftime('%B %-d, %Y %H:%M:%S'), flag_mask ), res)
            print("  Expected done_mask %x stale passes %x, date tests %x content tests %x" % (FM_ALL_DONE, FM_EXPECTED_STALE_PASSES, FM_DATE_TESTS, FM_CONTENT_TESTS))
            print(msgs)

            curDay = datetime.now().weekday()
            curHour = datetime.now().hour
            broadcastOK = curDay in chart_checker_tests.update_days and curHour in chart_checker_tests.update_hours

            broadcast_msg = ''

            # redo these dynamically
            chartdatebits = {}
            chartmatchbits = {}
            for ti, trec in enumerate(chart_tests):
                if trec['test_type'] == 'PASS':
                    continue
                elif 'DATE' in trec['test_type'] and 'WEEKLY' not in trec['test_type']:
                    chartdatebits[trec['bnom']] = ti
                else:
                    chartmatchbits[trec['bnom']] = ti
            big_broadcast = False
            if flag_mask == FM_EXPECTED_STALE_PASSES:  # check for typical morning staleness...
                pass
            elif flag_mask == FM_ALL_DONE:
                broadcast_msg = '/state-dashboard/ has been fully updated (charts match summaries, sparklines updated)'
                big_broadcast = True
                stale_alert_issued = False
            elif (flag_mask & FM_DATE_TESTS) == FM_DATE_TESTS and (flag_mask & FM_CONTENT_TESTS) != FM_CONTENT_TESTS:
                missmatched_items = [nom for nom,idx in chartmatchbits.items() if res[idx] == 0]
                broadcast_msg = '/state-dashboard/ has been fully updated, but %s charts don\'t match summaries' % ('/'.join(missmatched_items))
                big_broadcast = False
            else:
                updated_items_prev = [nom for nom,idx in chartdatebits.items() if (last_res_mask & (1 << idx))]
                updated_items_new = [nom for nom,idx in chartdatebits.items() if (flag_mask & (1 << idx))]
                new_items = list(set(updated_items_new).difference(set(updated_items_prev)))
                if last_res_mask == FM_EXPECTED_STALE_PASSES:
                    if len(new_items) > 0:
                        broadcast_msg = '/state-dashboard/ updates are starting (%s updated)' % (', '.join(new_items))
                    else:
                        broadcast_msg = '/state-dashboard/ updates are starting'
                    big_broadcast = True
                else:
                    if len(new_items) > 0:
                        broadcast_msg = '/state-dashboard/ has been partially updated (%s updated)' % (', '.join(new_items))
                    else:
                        broadcast_msg = '/state-dashboard/ has been partially updated'

            if broadcast_msg != '':
                if broadcastOK:
                    print("BROADCAST MESSAGE: %s" % (broadcast_msg))
                    if not args.quiet:
                        if args.test:
                            post_message_to_slack(broadcast_msg, channel=slackJimDebugChannel)
                        else:
                            if big_broadcast:
                                post_message_to_slack(broadcast_msg, channel=slackStateDashChannel)
                            post_message_to_slack(broadcast_msg, channel=slackAlertChannel)
                else:
                    print("INHIBITING BROADCAST: %s" % (broadcast_msg))
                    
            # post meaningful message to slack here...
        else:
            if args.verbose:
                print("No Change: res %02x" %(flag_mask))
            
        now = datetime.now().astimezone(timezone('US/Pacific'))
        if flag_mask != FM_ALL_DONE and now.hour == 9 and now.minute >= 55 and not stale_alert_issued:
            # issue stale alert
            print("STALE ALERT")
            stale_alert_issued = True
            if not args.quiet:
                # xian https://cadotgov.slack.com/team/U01KHGNK8KU
                # aaron https://cadotgov.slack.com/team/UQTUFH6FL
                # jbum U01ELJEJ1SM
                msg = "<@U01KHGNK8KU> <@UQTUFH6FL> <@U01ELJEJ1SM> State-Dash is still showing stale data after 9:50am!"
                post_message_to_slack(msg, channel=slackJimDebugChannel)
                send_pushover(msg)
                if not args.test:
                    post_message_to_slack(msg, channel=slackAlertChannel)


        last_res_mask = flag_mask
except KeyboardInterrupt:
    print('interrupted!')

time.sleep(1)        

'''
Got Status 10054
STATUS CHANGE October 12, 2021 09:06:50 10054 [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
['DATE_SUMMARY FAIL', 'DATE_CASES FAIL', 'MATCH_CASES_TOTAL PASS', 'DATE_DEATHS FAIL', 'MATCH_DEATHS_TOTAL PASS', 'DATE_TESTS FAIL', 'MATCH_TESTS PASS', 'DATE_GROUPS FAIL', 'DATE_POSITIVITY FAIL', 'DATE_PATIENTS FAIL', 'DATE_ICUBEDS FAIL', 'DATE_VACCINE_SPARKLINES_DATA FAIL', 'SPARKLINE_CASES FAIL', 'SPARKLINE_DEATHS FAIL', 'SPARKLINE_TESTS FAIL', 'SPARKLINE_VACCINES FAIL', 'DATE_POSTVAX PASS', '4/17 tests pass']
Sleeping 30
...
Got Status 10044
STATUS CHANGE October 12, 2021 09:09:05 10044 [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
['DATE_SUMMARY FAIL', 'DATE_CASES FAIL', 'MATCH_CASES_TOTAL PASS', 'DATE_DEATHS FAIL', 'MATCH_DEATHS_TOTAL !! exception', 'DATE_TESTS FAIL', 'MATCH_TESTS PASS', 'DATE_GROUPS FAIL', 'DATE_POSITIVITY FAIL', 'DATE_PATIENTS FAIL', 'DATE_ICUBEDS FAIL', 'DATE_VACCINE_SPARKLINES_DATA FAIL', 'SPARKLINE_CASES FAIL', 'SPARKLINE_DEATHS FAIL', 'SPARKLINE_TESTS FAIL', 'SPARKLINE_VACCINES FAIL', 'DATE_POSTVAX PASS', '3/16 tests pass']
BROADCAST MESSAGE: /state-dashboard/ updates are starting ( added)
Sleeping 30

Got Status 10054
STATUS CHANGE October 12, 2021 09:09:38 10054 [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
['DATE_SUMMARY FAIL', 'DATE_CASES FAIL', 'MATCH_CASES_TOTAL PASS', 'DATE_DEATHS FAIL', 'MATCH_DEATHS_TOTAL PASS', 'DATE_TESTS FAIL', 'MATCH_TESTS PASS', 'DATE_GROUPS FAIL', 'DATE_POSITIVITY FAIL', 'DATE_PATIENTS FAIL', 'DATE_ICUBEDS FAIL', 'DATE_VACCINE_SPARKLINES_DATA FAIL', 'SPARKLINE_CASES FAIL', 'SPARKLINE_DEATHS FAIL', 'SPARKLINE_TESTS FAIL', 'SPARKLINE_VACCINES FAIL', 'DATE_POSTVAX PASS', '4/17 tests pass']
Sleeping 30
...


Got Status 1006a
STATUS CHANGE October 12, 2021 09:21:30 1006a [0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
['DATE_SUMMARY FAIL', 'DATE_CASES PASS', 'MATCH_CASES_TOTAL FAIL', 'DATE_DEATHS PASS', 'MATCH_DEATHS_TOTAL FAIL', 'DATE_TESTS PASS', 'MATCH_TESTS PASS', 'DATE_GROUPS FAIL', 'DATE_POSITIVITY FAIL', 'DATE_PATIENTS FAIL', 'DATE_ICUBEDS FAIL', 'DATE_VACCINE_SPARKLINES_DATA FAIL', 'SPARKLINE_CASES FAIL', 'SPARKLINE_DEATHS FAIL', 'SPARKLINE_TESTS FAIL', 'SPARKLINE_VACCINES FAIL', 'DATE_POSTVAX PASS', '5/17 tests pass']
BROADCAST MESSAGE: /state-dashboard/ updates are starting (tests,deaths,cases added)
Sleeping 30

Got Status 1066a
STATUS CHANGE October 12, 2021 09:22:03 1066a [0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1]
['DATE_SUMMARY FAIL', 'DATE_CASES PASS', 'MATCH_CASES_TOTAL FAIL', 'DATE_DEATHS PASS', 'MATCH_DEATHS_TOTAL FAIL', 'DATE_TESTS PASS', 'MATCH_TESTS PASS', 'DATE_GROUPS FAIL', 'DATE_POSITIVITY FAIL', 'DATE_PATIENTS PASS', 'DATE_ICUBEDS PASS', 'DATE_VACCINE_SPARKLINES_DATA FAIL', 'SPARKLINE_CASES FAIL', 'SPARKLINE_DEATHS FAIL', 'SPARKLINE_TESTS FAIL', 'SPARKLINE_VACCINES FAIL', 'DATE_POSTVAX PASS', '7/17 tests pass']
BROADCAST MESSAGE: /state-dashboard/ has been partially updated (icu-beds,patients added)
Sleeping 30

Got Status 10f6a
STATUS CHANGE October 12, 2021 09:22:37 10f6a [0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1]
['DATE_SUMMARY FAIL', 'DATE_CASES PASS', 'MATCH_CASES_TOTAL FAIL', 'DATE_DEATHS PASS', 'MATCH_DEATHS_TOTAL FAIL', 'DATE_TESTS PASS', 'MATCH_TESTS PASS', 'DATE_GROUPS FAIL', 'DATE_POSITIVITY PASS', 'DATE_PATIENTS PASS', 'DATE_ICUBEDS PASS', 'DATE_VACCINE_SPARKLINES_DATA PASS', 'SPARKLINE_CASES FAIL', 'SPARKLINE_DEATHS FAIL', 'SPARKLINE_TESTS FAIL', 'SPARKLINE_VACCINES FAIL', 'DATE_POSTVAX PASS', '9/17 tests pass']
BROADCAST MESSAGE: /state-dashboard/ has been partially updated (positivity,vaccines-sparklines-data added)
Sleeping 30

...

Got Status 18f6a
STATUS CHANGE October 12, 2021 09:31:07 18f6a [0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1]
['DATE_SUMMARY FAIL', 'DATE_CASES PASS', 'MATCH_CASES_TOTAL FAIL', 'DATE_DEATHS PASS', 'MATCH_DEATHS_TOTAL FAIL', 'DATE_TESTS PASS', 'MATCH_TESTS PASS', 'DATE_GROUPS FAIL', 'DATE_POSITIVITY PASS', 'DATE_PATIENTS PASS', 'DATE_ICUBEDS PASS', 'DATE_VACCINE_SPARKLINES_DATA PASS', 'SPARKLINE_CASES FAIL', 'SPARKLINE_DEATHS FAIL', 'SPARKLINE_TESTS FAIL', 'SPARKLINE_VACCINES PASS', 'DATE_POSTVAX PASS', '10/17 tests pass']
BROADCAST MESSAGE: /state-dashboard/ has been partially updated (vaccines-sparkline added)
Sleeping 30

Got Status 18fea
STATUS CHANGE October 12, 2021 09:31:41 18fea [0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1]
['DATE_SUMMARY FAIL', 'DATE_CASES PASS', 'MATCH_CASES_TOTAL FAIL', 'DATE_DEATHS PASS', 'MATCH_DEATHS_TOTAL FAIL', 'DATE_TESTS PASS', 'MATCH_TESTS PASS', 'DATE_GROUPS PASS', 'DATE_POSITIVITY PASS', 'DATE_PATIENTS PASS', 'DATE_ICUBEDS PASS', 'DATE_VACCINE_SPARKLINES_DATA PASS', 'SPARKLINE_CASES FAIL', 'SPARKLINE_DEATHS FAIL', 'SPARKLINE_TESTS FAIL', 'SPARKLINE_VACCINES PASS', 'DATE_POSTVAX PASS', '11/17 tests pass']
BROADCAST MESSAGE: /state-dashboard/ has been partially updated (groups added)
Sleeping 30

...

Got Status 19fea
STATUS CHANGE October 12, 2021 09:36:48 19fea [0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1]
['DATE_SUMMARY FAIL', 'DATE_CASES PASS', 'MATCH_CASES_TOTAL FAIL', 'DATE_DEATHS PASS', 'MATCH_DEATHS_TOTAL FAIL', 'DATE_TESTS PASS', 'MATCH_TESTS PASS', 'DATE_GROUPS PASS', 'DATE_POSITIVITY PASS', 'DATE_PATIENTS PASS', 'DATE_ICUBEDS PASS', 'DATE_VACCINE_SPARKLINES_DATA PASS', 'SPARKLINE_CASES PASS', 'SPARKLINE_DEATHS FAIL', 'SPARKLINE_TESTS FAIL', 'SPARKLINE_VACCINES PASS', 'DATE_POSTVAX PASS', '12/17 tests pass']
BROADCAST MESSAGE: /state-dashboard/ has been partially updated (cases-sparkline added)
Sleeping 30

Got Status 1ffff
STATUS CHANGE October 12, 2021 09:39:38 1ffff [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
['DATE_SUMMARY PASS', 'DATE_CASES PASS', 'MATCH_CASES_TOTAL PASS', 'DATE_DEATHS PASS', 'MATCH_DEATHS_TOTAL PASS', 'DATE_TESTS PASS', 'MATCH_TESTS PASS', 'DATE_GROUPS PASS', 'DATE_POSITIVITY PASS', 'DATE_PATIENTS PASS', 'DATE_ICUBEDS PASS', 'DATE_VACCINE_SPARKLINES_DATA PASS', 'SPARKLINE_CASES PASS', 'SPARKLINE_DEATHS PASS', 'SPARKLINE_TESTS PASS', 'SPARKLINE_VACCINES PASS', 'DATE_POSTVAX PASS', '17/17 tests pass']
BROADCAST MESSAGE: /state-dashboard/ has been fully updated (charts match summaries, sparklines updated)

...

'''