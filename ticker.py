import requests
import twitter
#import sys
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

logging.basicConfig(filename='ticker.log',level=logging.INFO)
tweet_length = 280
hashtags = "#Hagen #VRR"
orte = ["MVG","VER","Dortmund","Schwerte","Iserlohn","Wiblingwerde","Breckerfeld","Ennepetal","Gevelsberg","Wetter","Herdecke","Kierspe"]
website = "http://www.strassenbahn-hagen.de"
tweet_length -= (len(website)+ 1 + len(hashtags))

knownfile = 'known-ticker.txt'

r = requests.get('http://www.strassenbahn-hagen.de/ticker_rss.xml')
root = ET.fromstring(r.content)

#tree = ET.parse(sys.argv[1])
#root = tree.getroot()

with open(knownfile,encoding='utf-8') as file:
    known = file.read().splitlines()

api = twitter.Api(consumer_key='X',
                  consumer_secret='X',
                  access_token_key='X',
                  access_token_secret='X')
#print(api.VerifyCredentials())

ci = 0
orig_content = []
tweets = []
for item in root.iter('item'):
    ci += 1
    content = " ".join(item[-1].text.split())
    orig_content.append(content)
    if content in known:
        continue
    title = ""
    if item.find('title').text is not None:
        title = BeautifulSoup(" ".join(item.find('title').text.split()).strip(), "lxml").text.strip()

    teile = content.split('<br>')
    map(str.strip, teile)

    ausgabe = ""
    ausgegeben = False
    bepunktet = False
    komma = ""

    for teil in teile:
        for unterteil in teil.split(". "): # potenzielles todo: anderes als punkt, hm
            if unterteil.find("keine Einschränkungen") < 0 and unterteil not in [""," ","\n"] and not (unterteil[0].lower() == "l" and ":" in [unterteil[-1],unterteil[-2]]):
                if teil.find(". ") > -1:
                    if bepunktet == False:
                        ausgabe += komma+unterteil.strip()
                        if ausgabe[-1] not in [".","!",";"]:
                            ausgabe += "."
                        ausgabe += " "
                        ausgegeben = True
                        bepunktet = True
                    else:
                        ausgabe += unterteil.strip()
                        if ausgabe[-1] not in [".","!",";"]:
                            ausgabe += "."
                        ausgabe += " "
                        ausgegeben = True
                        bepunktet = True
                else:
                    if bepunktet:
                        ausgabe += unterteil.strip()
                        ausgegeben = True
                        bepunktet = False
                    else:
                        ausgabe += komma+unterteil.strip()
                        ausgegeben = True
            if ausgegeben:
                if ausgabe[-1] in [".",",",")","!",";"]:
                    komma = " "
                else:
                    komma = ", "

    for ort in orte:
        ausgabe = ausgabe.replace(ort,"#"+ort)
    # todo: abgeschnittene hashtags soll es nicht geben
    # todo: kein #Dortmunder Str. etc.

    tweet = title+"\n"+ausgabe.strip()
    if tweet.count(" Linie ") > 3:
        tweet = tweet.replace(" Linie ","\nLinie ")

    tweetsplit = []
    if len(tweet) <= tweet_length:
        tweet += (" " + website + " " + hashtags)
        tweets.append([tweet])
        print(tweet)
    else:
        r = range(0, len(tweet), tweet_length-4)
        # todo: text pro tweet, insbesondere alle nach dem ersten, maximieren! ### 3 zu 4 geaendert
        for ri in r:
            if ri == r[-1]:
                tweetsplit.append("…"+tweet[ri:ri+tweet_length-4] + " " + website)
            elif ri == r[0]:
                tweetsplit.append(tweet[ri:ri+tweet_length-4] + "… " + website + " " + hashtags)
            else:
                tweetsplit.append("…"+tweet[ri:ri+tweet_length-4] + "… " + website)
            print(tweetsplit[-1])
        tweets.append(tweetsplit)

for x in tweets:
    ti = 0
    lastid = 0
    if len(x) == 1:
        try:
            status = api.PostUpdate(x[0])
        except Exception as e:
            logging.warning(str(datetime.now())+" "+str(e)+"\nContent:\n"+content+"\n")
        logging.info(str(datetime.now())+"\n\n"+x[0]+"\n\n")
    elif len(x) > 1:
        for tw in x:
            try:
                if ti == 0:
                    status = api.PostUpdate(tw)
                    lastid = status.id
                else:
                    status = api.PostUpdate(tw, in_reply_to_status_id=lastid)
                    lastid = status.id
            except Exception as e:
                logging.warning(str(datetime.now())+" x["+str(ti)+"] "+str(e)+"\nContent:\n"+content+"\n")
            ti += 1
        logging.info(str(datetime.now())+"\n\n"+"\n".join(x)+"\n\n")

with open(knownfile, 'w', encoding='utf-8') as file:
    if ci > 0:
        file.write('\n'.join(orig_content)+'\n')
    else:
        file.write('n\n')
