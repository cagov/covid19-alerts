# demandbot.py

import sys, time, argparse, importlib
from pytz import timezone
import requests, json

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
    if q['query'] not in wordbase:
        rec = {'query':q['query'], 'min':q['num'],  'max':0}
        wordbase[q['query']] = rec
        qrec = rec
    else:
        qrec = wordbase[q['query']]
    last_max = qrec['max']
    if q['num'] < qrec['min']:
        qrec['min'] = q['num']
    if q['num'] > qrec['max']:
        qrec['max'] = q['num']
    if last_max < 10 and qrec['max'] >= 10:
        reason = ''
        if wouldReject(q['query']):
            reason = 'trigger word'
        elif tooLong(q['query']):
            reason = 'too long'
        elif q['num'] <= 11:
            reason = 'low score'
        msg = "new search: %s%s" % ("<redacted>" if wouldReject(q['query']) else q['query'], 
                                    " (won't show: %s)" % (reason) if reason != '' else '')
        print("[DemandBot] " + msg)
        # advertise it...
        if not args.test and not args.quiet:
            post_message_to_slack(msg, channel=slackAlertChannel)
            post_message_to_slack(msg, channel=slackPageFeedbackChannel)

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

rejectList = [
	3154295, -891899646, 3446907, -1263686556,
	-519573749, 32245991, -1045620280, 3083181, 
	105116, 3059156, -717313205, -20842805,
	3529280, 3441177, 3065272, 3541578,
    -1220868373, -1734002494
]

def wouldReject(phrase):
    return len([1 for word in phrase.split(' ') if hashCode(word) in rejectList]) > 0

def tooLong(phrase):
    return phrase.count(' ') > 4


loadWordbase()

try:
    while True:
        sys.stdout.flush()
        if runs > 0:
            sleep_secs = 10 if args.test else 5*60
            time.sleep(sleep_secs)
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
