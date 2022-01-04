import argparse, re, subprocess, json, sys

# python3 field_history.py data/daily-stats-v2.json data.cases.LATEST_TOTAL_CONFIRMED_CASES

# python3 field_history.py data/daily-stats-v2.json data.vaccinations.CUMMULATIVE_DAILY_DOSES_ADMINISTERED data.cases.LATEST_TOTAL_CONFIRMED_CASES data.cases.LATEST_CONFIDENT_AVG_CASE_RATE_PER_100K_7_DAYS data.deaths.LATEST_TOTAL_CONFIRMED_DEATHS data.deaths.LATEST_CONFIDENT_AVG_DEATH_RATE_PER_100K_7_DAYS data.tests.LATEST_CONFIDENT_POSITIVITY_RATE_7_DAYS
# python3 field_history.py data/dashboard/vaccines/sparkline.json data.population.DAILY_AVERAGE data.population.TOTAL_VAXED_RATIO
# python3 field_history.py data/dashboard/confirmed-cases/california.json data.latest.CONFIRMED_CASES.CASES_DAILY_AVERAGE
# python3 field_history.py data/dashboard/confirmed-deaths/california.json data.latest.CONFIRMED_DEATHS.DEATHS_DAILY_AVERAGE

parser = argparse.ArgumentParser(description='Average CSV Daily')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose')
parser.add_argument('-t', '--test', default=False, action='store_true', help='Test')
parser.add_argument('-sd', '--start_date', default="2021-01-25", help='Start Date')
parser.add_argument('-o','--org',default='cagov',help="Org, default=%(default)s")
parser.add_argument('-r','--repo',default='covid-static-data',help="Repo, default=%(default)s")
# example data/daily-stats-v2.json
parser.add_argument('infile', help='Input JSON File')
parser.add_argument('fields', nargs='*', help='Field list')
args = parser.parse_args()

repo = args.repo

# this needs to be run from the covid-static-data directory
#

# for this file produce a list of checkins for the past 6 months (in order), sorted by timestamp.
# consider doing this with the API...
# git log --pretty=format:"%H - %ad" data/daily-stats-v2.json  (descending order, save the 1st from each date)

def get_field(jdata, field_name):
    f = jdata
    for nom in field_name.split('.'):
        f = f[nom]
    return f

cmd = "cd ../../%s; git log --pretty=format:\"%%H - %%ad\" '%s'; cd -" % (args.repo, args.infile)
if args.verbose:
    print("CMD: " + cmd)
res = subprocess.run(cmd, shell=True, check=True, capture_output=True)
# print("res",res)
last_date = None
commit_list = []
for linein in res.stdout.split(b'\n'):
    line = linein.decode('utf-8')
    # fc406d58f9913044a5cb47746ba5aba9280ecaa8 - Sat May 15 09:05:10cd  2021 -0700
    m = re.match(r'^([a-f0-9]+) - (\w\w\w \w\w\w \d+) (\d\d:\d\d:\d\d) (\d\d\d\d)', line)
    if m:
        commit_id = m.group(1)
        date_str = m.group(2)
        time_str = m.group(3)
        year_str = m.group(4)
        daily_str = date_str+' '+year_str
        # reject all temporary checkins for which there is a later check-in on the same date.
        #
        if last_date == None or last_date != daily_str:
            last_date = daily_str
            # print(commit_id, date_str, year_str)
            commit_list.append((commit_id,daily_str))
    else:
        if args.verbose:
            print("Mismatch '%s'\n" % (line))

if args.verbose:
    print("LAST DATE: ", commit_list[0])

report = {}

for fldname in args.fields:
    report[fldname] = {'min_val':None, 'max_val':None,'min_change':0, 'max_change':0,'min_factor':0,'max_factor':0,'last_v':None}

cnt = 0
for commit_id,commit_date in reversed(commit_list):
    if args.verbose:
        print("Commit_ID",commit_id)
    cmd = "curl -s https://raw.githubusercontent.com/%s/%s/%s/%s" % (args.org, args.repo, commit_id,args.infile)
    # print(cmd)
    if args.test:
        print(cmd)
    res = subprocess.run(cmd, shell=True, check=True, capture_output=True)
    try:
        jdata = json.loads(res.stdout)
    except Exception as e:
        print("%s skipped due to json error" % (commit_date))
        continue
    for fldname in args.fields:
        try:
            v = get_field(jdata, fldname)
        except Exception as e:
            continue
        if args.verbose:
            print(fldname, get_field(jdata, fldname))
        rep = report[fldname]
        if (args.verbose):
            print("Date: %s " % (commit_date),v)
        if rep['last_v'] == None:
            rep['min_val'] = v
            rep['max_val'] = v
            rep['changes'] = 0
            rep['records'] = 0
        else:
            rep['min_val'] = min(rep['min_val'], v)
            rep['max_val'] = max(rep['max_val'], v)
            if v / rep['last_v'] - 1 < 1 and v / rep['last_v'] - 1 > -1: # throw out anomalies
                rep['min_change'] = min(v-rep['last_v'], rep['min_change'])
                rep['max_change'] = max(v-rep['last_v'], rep['max_change'])
                rep['max_factor'] = max(v / rep['last_v'] - 1, rep['max_factor'])
                rep['min_factor'] = min(v / rep['last_v'] - 1, rep['min_factor'])
            rep['records'] += 1
            if v != rep['last_v']:
                rep['changes'] += 1
        rep['last_v'] = v
    cnt += 1
    if args.test and cnt > 5:
        break

for fldname in args.fields:
    print("\nFIELD: " + fldname)
    rep = report[fldname]
    # print("Val Range    %.1f - %.1f Change Range %.1f - %.1f Growth Range %% %.4f - %.4f" % (
    #             float(min_val), float(max_val),
    #             float(min_change), float(max_change),
    #             float(min_factor)*100, float(max_factor)*100
    #             ))
    if abs(rep['min_val'] - rep['max_val']) < 1:
        print("(%.5f, %.5f,  %.5f, %.5f,   %.5f, %.5f, %5.2f)" % (
                float(rep['min_val']), float(rep['max_val']),
                float(rep['min_change']), float(rep['max_change']),
                float(rep['min_factor']), float(rep['max_factor']),
                float(rep['changes'])*100.0/float(rep['records'])
                ))
    else:
        print("(%.1f, %.1f,  %.1f, %.1f,   %.6f, %.6f, %5.2f)" % (
                float(rep['min_val']), float(rep['max_val']),
                float(rep['min_change']), float(rep['max_change']),
                float(rep['min_factor']), float(rep['max_factor']), 
                float(rep['changes'])*100.0/float(rep['records'])
                ))

# for each checkin, sorted by date-asc, read the raw file for that checkin and store the value.
# https://raw.githubusercontent.com/<REPO>/<LONG_COMMIT_NO>/<FILENAME>data/daily-stats-v2.json

# if the field is not present, or over a year old, skip

# produce a report of min/max ascending and descending deltas, and min/max asc/desc factors.
# produce recommended limits based on those values (5x the max)
