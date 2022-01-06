# deltabot
import sys, time, argparse, importlib
import requests, json
from datetime import datetime, timedelta
from pytz import timezone

# reopen stdout as utf-8, to avoid encoding errors on console messages
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

parser = argparse.ArgumentParser(description='deltabot')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose')
parser.add_argument('-vv', '--very_verbose', default=False, action='store_true', help='Very Verbose')
parser.add_argument('-t', '--test', default=False, action='store_true', help='Test - broadcast to testingbot only')
parser.add_argument('-q', '--quiet', default=False, action='store_true', help='No broadcasting')
parser.add_argument('-go','--org',default='cagov',help="Org, default=%(default)s")
parser.add_argument('-gr','--repo',default='covid-static-data',help="Repo, default=%(default)s")
parser.add_argument('-b', '--branch_override', default=None, help='Branch to read, default=%(default)s')
parser.add_argument('-r', '--reset', default=False, action='store_true', help='Reset to current data')
parser.add_argument('-config', default="deltabot_config", help='Config file name prefix, default=%(default)s')
args = parser.parse_args()

if args.very_verbose:
    args.verbose = True

dbot_config = importlib.import_module(args.config)
from slack_credentials import slackbot_token
from slack_info import slackAlertChannel, slackJimDebugChannel

def post_message_to_slack(text, blocks = None, channel=slackJimDebugChannel):
    res = requests.post('https://slack.com/api/chat.postMessage', {
        'token': slackbot_token,
        'channel': channel,
        'text': "[DeltaBot] " + text,
        'icon_emoji': ':small_red_triangle:',
        'unfurl_links': False,
        'unfurl_media': False,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()
    if args.verbose:
        print(res)
    return res


# load the json...
deltabase = {}
delta_changes = False

def loadDeltabase():
    global deltabase, delta_changes
    try:
        deltabase = json.load(open(dbot_config.deltabase_name))
        delta_changes = False
    except Exception as e:
        print("Initializing wordbase")
        deltabase = {}
        delta_changes = True
        pass

def saveDeltabase():
    global deltabase, delta_changes
    if delta_changes:
        if not args.test: # don't save when testing...
            with open(dbot_config.deltabase_name,'w') as outfile:
                json.dump(deltabase, outfile, indent=2)
        delta_changes = False

def get_field(jdata, field_name):
    f = jdata
    for nom in field_name.split('.'):
        f = f[nom]
    return f


def perform_warning(filerec, fieldrec, old_value, new_value, warnmessage, channel=slackAlertChannel):
    # add after debugging: <@U01KHGNK8KU> <@UQTUFH6FL> <@U01ELJEJ1SM> 
    # xian https://cadotgov.slack.com/team/U01KHGNK8KU
    # aaron https://cadotgov.slack.com/team/UQTUFH6FL
    # jbum https://cadotgov.slack.com/team/U01ELJEJ1SM

    # sample link: https://github.com/cagov/covid-static-data/blob/test_deltabot/data/daily-stats-v2.json
    file_link = 'https://github.com/%s/%s/blob/%s/%s' % (args.org, args.repo, filerec['branch'], filerec['filename'])
    message = '''<@U01ELJEJ1SM>
 %s %s
 File: %s
 Field: %s
 ```
 Previous value: %s
 New value     : %s```
    ''' % (fieldrec['desc'], warnmessage, 
           file_link,
           fieldrec['field'], 
           str(old_value), 
           str(new_value))
    if not args.quiet:
        post_message_to_slack(message, channel=channel)
    else:
        print("Would post warning\n%s" % (message))
    if args.verbose:
        print("Posting warning about %s %s" % (filerec['filename'], fieldrec['field']))

# UNUSED
def is_weekday():
    global dbot_config
    now = datetime.now().astimezone(timezone('US/Pacific'))
    fulldate = now.strftime('%Y-%m-%d')
    dayofweek = now.strftime('%a')
    if fulldate in dbot_config.holidays:
        return False
    return dayofweek in ('Mon','Tue','Wed','Thu','Fri')

loadDeltabase()
runs = 0

try:
    while True:
        sys.stdout.flush()
        if runs > 0:
            now = datetime.now().astimezone(timezone('US/Pacific'))
            if now.hour >= 7 and now.hour < 10:
                sleep_secs = dbot_config.busy_sleep
            else:
                sleep_secs = dbot_config.offhours_sleep
            if args.verbose:
                print("Sleeping",sleep_secs)
            time.sleep(sleep_secs)
        runs += 1

        # reload config
        importlib.reload(dbot_config)

        # perform tests here...
        # call updateDeltabase as necessary
        for file_rec in dbot_config.file_list:
            if args.verbose:
                print("Processing %s" % (file_rec['filename']))
            filename = file_rec['filename']
            branch = args.branch_override if args.branch_override else file_rec['branch']
            # read filename from branch (or use branch override)
            url = 'https://raw.githubusercontent.com/%s/%s/%s/%s' % (
                args.org, args.repo, branch, filename
            )
            jr = requests.get(url)
            curdata = json.loads(jr.text)

            if filename in deltabase and not args.reset:
                old_date = datetime.strptime(get_field(deltabase[filename], file_rec['pdate_field']),'%Y-%m-%d')
                new_date = datetime.strptime(get_field(curdata, file_rec['pdate_field']),'%Y-%m-%d')
                if new_date <= old_date:
                    if new_date < old_date:
                        print("Date went backwards, ignoring")
                    else:
                        if args.verbose:
                            print("File %s is unchanged" % (filename))
                    continue
                # do field by field comparisons here...
                if args.verbose:
                    print("File %s has changed, checking" % (filename))
                issues_found = 0
                for frec in file_rec['fields_of_interest']:
                    if 'date_check' in frec:
                        old_fdate = get_field(deltabase[filename], frec['date_check'])
                        new_fdate = get_field(curdata, frec['date_check'])
                        if new_fdate == old_fdate:
                            if args.verbose:
                                print("Field %s date is unchanged" % (frec['field']))
                            continue
                    old_value = get_field(deltabase[filename], frec['field'])
                    new_value = get_field(curdata, frec['field'])
                    if old_value == new_value and \
                        'always_changes' in frec['flags']:
                        perform_warning(file_rec, frec, old_value, new_value, "has not changed, but was expected to")
                        issues_found += 1
                    min_value, max_value, min_change, max_change, min_growth, max_growth = frec['params']
                    delta = new_value - old_value
                    try:
                        growth = (new_value / old_value) - 1.0
                    except Exception as e:
                        growth = 0
                    # deaths daily average: TRIGGER SINK: old: 45.285714 new: 40.857143 delta: -4.428571 growth: -0.097792 min_change -0.01950, min_growth: -0.12003

                    if growth < dbot_config.trigger_factor * min_growth:
                        if args.verbose:
                            print("TRIGGER SINK %s: old: %f new: %f delta: %f growth: %f min_change %.5f, min_growth: %.5f\n" % (frec['desc'], old_value, new_value, delta, growth, min_change, min_growth))
                        perform_warning(file_rec, frec, old_value, new_value, 
                                "has sunk at least %.1fx faster than ever seen before" % (dbot_config.trigger_factor))
                        issues_found += 1
                    elif growth < 1.1*min_growth:
                        perform_warning(file_rec, frec, old_value, new_value, 
                                "has sunk faster than seen before - time to update config?", channel=slackJimDebugChannel)
                        issues_found += 1
                    if growth > dbot_config.trigger_factor * max_growth:
                        if args.verbose:
                            print("TRIGGER RISE %s: old: %f new: %f delta: %f growth: %f max_change %.5f, max_growth: %.5f\n" % (frec['desc'], old_value, new_value, delta, growth, max_change, max_growth))
                        perform_warning(file_rec, frec, old_value, new_value, 
                                "has risen at least %.1fx faster than ever seen before" % (dbot_config.trigger_factor))
                        issues_found += 1
                    elif growth > 1.1*max_growth:
                        perform_warning(file_rec, frec, old_value, new_value, 
                                "has risen faster than seen before - time to update config?", channel=slackJimDebugChannel)
                        issues_found += 1
            else:
                if args.reset:
                    print("%s reset" % (filename))
                else:
                    print("%s is not in deltabase" % (filename))

            deltabase[filename] = curdata
            delta_changes = True
            args.reset = False

        saveDeltabase()
        # print(data)
except KeyboardInterrupt:
    print('interrupted!')

time.sleep(1)        
