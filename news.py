import requests
import twitter
import logging
#import sys
from datetime import datetime
import xml.etree.ElementTree as ET

logging.basicConfig(filename='news.log',level=logging.INFO)
tweet_length = 280
hashtags = "#Hagen #VRR"
tweet_length -= len(hashtags)

knownfile = 'known-news.txt'

r = requests.get('http://www.strassenbahn-hagen.de/news_rss.xml')
root = ET.fromstring(r.content)

#tree = ET.parse(sys.argv[1])
#root = tree.getroot()

with open(knownfile) as file:
    known = file.read().splitlines()
nowknown = []

api = twitter.Api(consumer_key='X',
                  consumer_secret='X',
                  access_token_key='X',
                  access_token_secret='X')
#print(api.VerifyCredentials())

for item in root.iter('item'):
    guid = item[0].text
    nowknown.append(guid)

    if guid in known:
        continue
    #else:
    #    with open(knownfile, 'a') as file:
    #        file.write(guid+'\n')

    link = item.find('link').text
    title = item.find('title').text

    rest_length = tweet_length - len(title) - len(link)

    tweet = title+" "+link+" "+hashtags

    try:
        status = api.PostUpdate(tweet)
    except Exception as e:
        logging.warning(str(datetime.now())+str(e))

    logging.info(str(datetime.now())+" "+guid+" "+str(rest_length)+"\n\n"+tweet+"\n\n")

# neu:
with open(knownfile, 'w', encoding='utf-8') as file:
    file.write('\n'.join(nowknown)+'\n')
