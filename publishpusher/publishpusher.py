# publishpusher
#
import sys, time, argparse, importlib
from pytz import timezone
import requests
from datetime import datetime
from pytz import timezone

# reopen stdout as utf-8, to avoid encoding errors on console messages
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

parser = argparse.ArgumentParser(description='demandbot')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose')
parser.add_argument('-vv', '--very_verbose', default=False, action='store_true', help='Very Verbose')
parser.add_argument('-t', '--test', default=False, action='store_true', help='Test - broadcast to testingbot only')
parser.add_argument('-q', '--quiet', default=False, action='store_true', help='No broadcasting')
parser.add_argument('-config', default="publishpusher_config", help='Config file name prefix, default=%(default)s')
args = parser.parse_args()

if args.very_verbose:
    args.verbose = True

pp_config = importlib.import_module(args.config)

runs = 0
try:
    while True:
        sys.stdout.flush()
        if runs > 0:
            time.sleep(pp_config.push_interval_secs)

        runs += 1
        pp_config = importlib.import_module(args.config)
        dateTimeObj = datetime.now().astimezone(timezone('US/Pacific'))
        curHour = dateTimeObj.hour
        if curHour >= pp_config.first_active_hour and curHour <= pp_config.last_active_hour:
            if not args.quiet:
                print(dateTimeObj, "Triggering")
            post_params = {'polldate':str(dateTimeObj)}
            jr = requests.post(pp_config.trigger_url, data=post_params)
        # print(data)
except KeyboardInterrupt:
    print('interrupted!')

time.sleep(1)        
