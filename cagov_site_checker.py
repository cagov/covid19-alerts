# check site for useful stuff

import re, sys, os, time, argparse, importlib, hashlib, random
# import mechanicalsoup
from datetime import datetime
from jbum_pushover import pushover_app_token, pushover_user_key
import http.client, urllib
import requests, json
# import redis
from lxml import etree

from slack_credentials import slackbot_token
from slack_info import slackAlertChannel, slackTeamID


parser = argparse.ArgumentParser(description='Cagov site checker')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose')
parser.add_argument('-t', '--test', default=False, action='store_true', help='Test')
parser.add_argument('-q', '--quiet', default=False, action='store_true', help='Quiet - no slack')
parser.add_argument('-n', '--no_init_sleep', default=False, action='store_true', help='No initial sleep')
parser.add_argument('-config', default="cagov_config", help='Config file name prefix, default=%(default)s')
args = parser.parse_args()


# r = redis.StrictRedis(host='localhost', port=6379, db=0)

cagov_config = importlib.import_module(args.config)

def post_message_to_slack(text, blocks = None, channel=slackAlertChannel):
    if not args.quiet:
        requests.post('https://slack.com/api/chat.postMessage', {
            'token': slackbot_token,
            'channel': channel,
            'text': text,
            'icon_emoji': ':butterfly:',
            # 'icon_url': slack_icon_url,
            # 'username': slack_user_name,
            'blocks': json.dumps(blocks) if blocks else None
        }).json()
    else:
        print("Would post", text)


def send_pushover(message, title='CAGOVAlert', url=None, url_title=None):
    global args
    try:
        print("Broadcasting message:",message)
        if args.test or args.quiet:
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
runs = 0
old_pages = {}
old_statuses = {}
# sys.exit()

try:
    while True:
        sys.stdout.flush()
        if not(args.no_init_sleep and runs == 0):
            # random sleep
            sleep_secs = random.randrange(cagov_config.min_sleep, cagov_config.max_sleep)
            if args.verbose:
                print("Sleeping",sleep_secs)
            time.sleep(sleep_secs)

        importlib.reload(cagov_config)

        # pull site map here...
        url = cagov_config.root_url + '/sitemap.xml'
        url_title = '/sitemap.xml'
        page_noms = []
        pages_updated = []
        pages_published = []
        try:
            r = requests.get(url)
            if r.status_code != 200:
                if url in old_statuses and old_statuses[url] != r.status_code:
                    # post_message_to_slack("Non 200 result for %s (%d)" % (url_title, r.status_code), channel=slackOutagesChannel)
                    post_message_to_slack("<@U03G2SJ2PEY> <@U01ELJEJ1SM> Non 200 result for %s (%d)" % (url_title, r.status_code), channel=slackAlertChannel)
                    send_pushover("Non-200 result for %s (%d)" % (url_title, r.status_code),url=url,url_title=url_title)
                    time.sleep(60)
                old_statuses[url] = r.status_code
                continue
            old_statuses[url] = r.status_code

            root = etree.fromstring(r.content)
            for sitemap in root:
                children = sitemap.getchildren()
                purl = children[0].text
                if not re.search(r'\/(ar|es|ko|tl|vi|zh-hans|zh-hant)\/', purl):
                    page_noms.append(purl.replace(cagov_config.root_url,''))
            if args.verbose:
                print(page_noms)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            send_pushover("a Error retrieving sitemap.xml",url=url,url_title=url_title)
            # post_message_to_slack("Error retrieving %s" % (url_title))
            time.sleep(60)
            continue

        # browser = mechanicalsoup.StatefulBrowser()
        for page_nom in page_noms:
            url, url_title = (cagov_config.root_url+page_nom, page_nom)
            if args.verbose:
                print("Checking",url)
            try:
                r = requests.get(url)
                text = r.text
                for pat in cagov_config.removals:
                    text = re.sub(pat,'',text)
                for pat,rep in cagov_config.replacements:
                    text = re.sub(pat,rep,text)
                if args.test:
                    ofilename = page_nom.replace("/","") + '.html'
                    with open("./pages/" +ofilename,"w") as ofile:
                        ofile.write(text)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e)
                send_pushover("b Error retrieving %s" % (url_title),url=url,url_title=url_title)
                # post_message_to_slack("Error retrieving %s" % (url_title))
                time.sleep(1)
                continue

            if r.status_code != 200:
                if url in old_statuses and old_statuses[url] != r.status_code:
                    # post_message_to_slack("Non 200 result for %s (%d)" % (url_title, r.status_code), channel=slackOutagesChannel)
                    post_message_to_slack("<@U03G2SJ2PEY> <@U01ELJEJ1SM> Non 200 result for %s (%d)" % (url_title, r.status_code), channel=slackAlertChannel)
                    send_pushover("Non-200 result for %s (%d)" % (url_title, r.status_code),url=url,url_title=url_title)
                    time.sleep(1)
                old_statuses[url] = r.status_code
                continue
            # use a memcache here...
            if url in old_pages and old_pages[url] != text:
                pages_updated.append(url_title)
            elif url not in old_pages and runs > 1:
                pages_published.append(url_title)
            old_pages[url] = text
            old_statuses[url] = r.status_code
            time.sleep(1)
        runs += 1
        if len(pages_published) > 0:
            if len(pages_published) > 5:
                post_message_to_slack("%d pages published" % (len(pages_published)),channel=slackAlertChannel)
            else:
                post_message_to_slack("%s published" % (','.join(pages_published)),channel=slackAlertChannel)
            send_pushover("%s published" % (','.join(pages_published)))
        if len(pages_updated) > 0:
            if len(pages_updated) > 5:
                post_message_to_slack("%d pages updated" % (len(pages_updated)),channel=slackAlertChannel)
            else:
                post_message_to_slack("%s updated" % (','.join(pages_updated)),channel=slackAlertChannel)
            send_pushover("%s Updated" % (','.join(pages_updated)))
        elif args.verbose:
            print("All sites passed")
        # if runs == 2 and args.test:
        #     sys.exit()
except KeyboardInterrupt:
    print('interrupted!')

time.sleep(1)
