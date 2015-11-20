import json
import urllib2
import time
import csv
import re
import argparse



def loadPage(url):
    # delay
    time.sleep(1)
    # download
    response = urllib2.urlopen(url)
    content = response.read()
    payload = ''
    print "DOWNLOAD!"
    try:
        payload = json.loads(content)
    except:
        print "JSON decoding failed!"
    if 'data' in payload:
        out = []
        for post in payload['data']:
            if 'message' in post:
                # make timestamp pretty
                timestamp = post['created_time']
                timestamp = re.sub(r'\+\d+$', '', timestamp)
                timestamp = timestamp.replace('T',' ')
                out.append({
                    'author': post['from']['name'].encode('ascii', 'ignore'),
                    'timestamp': timestamp,
                    'message': post['message'].encode('ascii', 'ignore')})
        out2 = []
        if 'paging' in payload:
            out2 = loadPage(payload['paging']['next'])
        return out + out2
    return []
    

# entry point:

# # get args
# parser = argparse.ArgumentParser()
# parser.add_argument('id', help='ID of Graph API resource')
# parser.add_argument('-o', '--out', default="fbdump.csv", help='Output file')
# parser.add_argument('-t', '--token', help='Authentication token')
# args = parser.parse_args()
def fb2csv(fb_id, output_file, token):


    try:
        out = loadPage("https://graph.facebook.com/%s/feed?fields=from,message&access_token=%s" % (fb_id, token))
        print len(out)
        # write output to file
        with open(output_file, 'w') as csvfile:
            fieldnames = ['message', 'author']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for elem in out:
                writer.writerow(elem)
    except urllib2.HTTPError as e:
        print "Download failed:",e
        error_message = e.read()
        print error_message
    except KeyboardInterrupt:
        print "Canceled!"