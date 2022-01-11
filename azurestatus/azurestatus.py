# status reporter
#

import sys, time, argparse, importlib
from pytz import timezone
import requests, json
import mechanicalsoup

# reopen stdout as utf-8, to avoid encoding errors on console messages
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

parser = argparse.ArgumentParser(description='azurestatus')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose')
parser.add_argument('-vv', '--very_verbose', default=False, action='store_true', help='Very Verbose')
parser.add_argument('-t', '--test', default=False, action='store_true', help='Test - broadcast to testingbot only')
parser.add_argument('-q', '--quiet', default=False, action='store_true', help='No broadcasting')
parser.add_argument('-config', default="azurestatus_config", help='Config file name prefix, default=%(default)s')
args = parser.parse_args()

if args.very_verbose:
    args.verbose = True

az_config = importlib.import_module(args.config)
from slack_credentials import slackbot_token
from slack_info import slackAlertChannel, slackStateDashChannel, slackJimDebugChannel, slackPageFeedbackChannel

def post_message_to_slack(text, blocks = None, channel=slackJimDebugChannel):
    res = requests.post('https://slack.com/api/chat.postMessage', {
        'token': slackbot_token,
        'channel': channel,
        'text': "[Azurebot] " + text,
        'icon_emoji': ':small_blue_diamond:',
        # 'icon_url': slack_icon_url,
        # 'username': slack_user_name,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()
    if args.verbose:
        print(res)
    return res

azbase = {}

def loadAZbase():
    global azbase
    try:
        azbase = json.load(open(az_config.azbase_name))
    except Exception as e:
        print("Initializing azbase")
        wordbase = {}
        pass

def saveAZbase():
    global azbase
    with open(az_config.azbase_name,'w') as outfile:
        json.dump(azbase, outfile, indent=2)


# fetch the page
runs = 0


loadAZbase()

try:
    while True:
        sys.stdout.flush()
        if runs > 0:
            sleep_secs = az_config.test_sleep if args.test else az_config.normal_sleep
            time.sleep(az_config.normal_sleep)
        runs += 1

        browser = mechanicalsoup.StatefulBrowser()
        browser.open(az_config.azurestatus_url)
        soup = browser.get_current_page()

        # data-zone-name="americas" class="status-table
        # <table data-zone-name="americas" class="status-table region-status-table default">

        main_cat = ''
        sub_cat = ''

        changes_occured = False

        for tab in soup.find_all('table',attrs={"data-zone-name": "americas"},class_='status-table region-status-table default'):
            if args.verbose:
                print("Got Table")
            rowlabels = [th.span.text for th in tab.thead.tr.find_all('th')]
            if args.verbose:
                print("ROW LABELS",rowlabels)

            for tr in tab.tbody.find_all('tr'):
                if 'status-category' in tr.get_attribute_list('class'):
                    # it's just a label
                    if args.very_verbose:
                        print("Skipping status category",tr.td.text.strip())
                    continue
                if 'capability-row' in tr.get_attribute_list('class'):
                    if args.very_verbose:
                        print("GOT SUBCAT",tr.td.text.strip())
                    sub_cat = tr.td.text.strip()
                else:
                    main_cat = tr.td.text.strip()
                    sub_cat = ''
                if args.very_verbose:
                    print("Looking at %s / %s" % (main_cat, sub_cat))
                for i,td in enumerate(tr.find_all('td')):
                    if i == 0:
                        continue
                    if 'status-cell' in td.get_attribute_list('class'):
                        key = "%s/%s/%s" % (main_cat, sub_cat, rowlabels[i])
                        label = td.span['data-label']
                        if key not in azbase or azbase[key] != label:
                            if key in azbase:
                                # report status change
                                if not args.quiet:
                                    post_message_to_slack("%s: %s" % (key,label))
                            azbase[key] = label
                            changes_occured = True
                            if args.verbose:
                                print("%s / %s (%s) %s" % (main_cat, sub_cat, rowlabels[i], label))
        if changes_occured and not args.test:
            saveAZbase()
        # print(data)
except KeyboardInterrupt:
    print('interrupted!')

time.sleep(1)        
