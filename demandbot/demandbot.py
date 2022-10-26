# demandbot.py

import sys, time, argparse, importlib
import re
import requests, json
from pytz import timezone
from datetime import datetime

# reopen stdout as utf-8, to avoid encoding errors on console messages
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

parser = argparse.ArgumentParser(description='demandbot')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose')
parser.add_argument('-vv', '--very_verbose', default=False, action='store_true', help='Very Verbose')
parser.add_argument('-t', '--test', default=False, action='store_true', help='Test - broadcast to testingbot only')
parser.add_argument('-q', '--quiet', default=False, action='store_true', help='No broadcasting')
parser.add_argument('-config', default="demandbot_config", help='Config file name prefix, default=%(default)s')
args = parser.parse_args()

if args.very_verbose:
    args.verbose = True

dbot_config = importlib.import_module(args.config)
from slack_credentials import slackbot_token
from slack_info import slackAlertChannel, slackStateDashChannel, slackJimDebugChannel, slackPageFeedbackChannel

def post_message_to_slack(text, blocks = None, channel=slackJimDebugChannel):
    res = requests.post('https://slack.com/api/chat.postMessage', {
        'token': slackbot_token,
        'channel': channel,
        'text': "[DemandBot] " + text,
        'icon_emoji': ':mag:',
        # 'icon_url': slack_icon_url,
        # 'username': slack_user_name,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()
    if args.verbose:
        print(res)
    return res


# load the json...
wordbase = {}

def loadWordbase():
    global wordbase
    try:
        wordbase = json.load(open(dbot_config.wordbase_name))
    except Exception as e:
        print("Initializing wordbase")
        wordbase = {}
        pass

def updateWordbase(q):
    global wordbase
    ts = datetime.now().astimezone(timezone('US/Pacific')).timestamp()


    if q['query'] not in wordbase:
        rec = {'query':q['query'], 'min':q['num'],  'max':0, 'ts':ts}
        wordbase[q['query']] = rec
        qrec = rec
    else:
        qrec = wordbase[q['query']]
        if 'ts' not in qrec:
            qrec['ts'] = ts
    last_max = qrec['max']
    elapsed = ts - qrec['ts']
    qrec['min'] = min(q['num'],qrec['min'])
    qrec['max'] = max(q['num'],qrec['max'])
    qrec['ts'] = ts
    # if last_max < 10 and qrec['max'] >= 10:
    if args.verbose:
        print("query", q['query'], "elapsed",elapsed)
    if elapsed > dbot_config.elapsed_window or last_max < 10 and qrec['max'] >= 10:
        reason = ''
        if wouldReject(q['query']):
            reason = 'trigger word'
        elif tooLong(q['query']):
            reason = 'too long'
        elif tooShort(q['query']):
            reason = 'too short'
        elif looksLikeEmailOrDomain(q['query']):
            reason = 'looks like email or domain name'
        elif q['num'] <= 10:
            reason = 'low score'
        msg = "new search: %s%s" % ("<redacted>" if wouldReject(q['query']) else q['query'], 
                                    " (won't show: %s)" % (reason) if reason != '' else '')
        print("[DemandBot] " + msg)
        # advertise it...
        if not args.test and not args.quiet:
            post_message_to_slack(msg, channel=slackAlertChannel)
            # post_message_to_slack(msg, channel=slackPageFeedbackChannel)

def saveWordbase():
    global wordbase
    with open(dbot_config.wordbase_name,'w') as outfile:
        json.dump(wordbase, outfile, indent=2)

def hashCode(w):
    hash = 0
    if len(w) == 0:
        return hash
    for chr in w:
        hash = ((hash << 5) - hash) + ord(chr)
        hash &= 0xFFFFFFFF
    if hash & 0x80000000:
        hash -= 0x100000000
    return hash

#                 jr = requests.get(url)
#                data = json.loads(jr.text)
runs = 0

def wouldReject(phrase):
    global dbot_config
    if hashCode(phrase) in dbot_config.rejectList:
        return True
    return len([1 for word in phrase.split(' ') if hashCode(word) in dbot_config.rejectList]) > 0

def looksLikeEmailOrDomain(phrase):
    return re.search(r'((@|\w+\.\w+))', phrase) != None

def tooLong(phrase):
    return phrase.count(' ') > 4

def tooShort(phrase):
    return len(phrase) < 4

loadWordbase()

try:
    while True:
        sys.stdout.flush()
        if runs > 0:
            sleep_secs = 10 if args.test else 30*60
            time.sleep(sleep_secs)
        importlib.reload(dbot_config)
        runs += 1
        url = dbot_config.searches_url
        jr = requests.get(url)
        json_text = jr.text.replace('\\x','%')
        data = json.loads(json_text)
        for q in data['popularQueries']:
            if args.very_verbose:
                print("%-3d %s reject=%s (%d)" % (q['num'],q['query'],wouldReject(q['query']), hashCode(q['query'])))
            updateWordbase(q)
        saveWordbase()
        # print(data)
except KeyboardInterrupt:
    print('interrupted!')

time.sleep(1)        
