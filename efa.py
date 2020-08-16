import requests
import twitter
#import sys
from datetime import datetime
import logging
import xml.etree.ElementTree as ET

logging.basicConfig(filename='efa.log',level=logging.INFO)
tweet_length = 280
hashtags = "#VRR"
tweet_length -= len(hashtags)

knownfile = 'known-efa.txt'

payload = {'language':'de',
           'itdLPxx_transpCompany':'vrr',
           'filterPublicationStatus':'current',
           'filterOMC_PlaceID':'5914000:29',
#           'itdLPxx_selOperator':'HST', nicht gut wegen 00 Sonstige
           'filterProviderCode':'HST',
           'AIXMLReduction':['removeStops','removeLines','removeValidity','removePublication','removeCreationTime','removeExpirationTime','removeSourceSystem']}
r = requests.get('http://openservice-test.vrr.de/static02/XML_ADDINFO_REQUEST',payload)
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
titles = []
for itdATI in root.iter('itdAdditionalTravelInformation'):
    ci += 1
    infoID = itdATI.attrib['infoID']
    infolinktext = itdATI[0].find('infoLinkText').text
    # war vorher mit infoID statt text

    titles.append(infolinktext)
    if infolinktext in known:
        continue

    timespan = "("+itdATI[0][0][-1].find('value').text+")"
    #link = itdATI[0].find('infoLinkURL').text   # URL mit IP schlecht bei Twitter
    link = "https://efa.vrr.de/vrr/XSLT_ADDINFO_REQUEST?itdLPxx_addInfoDetailView="+infoID

    rest_length = tweet_length - len(timespan) - len(link)

    smstext = ""

    if itdATI[0].find('infoText').find('outputClientText').find('smsText') is not None:
        smstext = itdATI[0].find('infoText').find('outputClientText')[0].text
    
    if len(infolinktext) <= rest_length:
        outputtext = infolinktext
    elif len(smstext) <= rest_length and len(smstext) != 0:
        outputtext = smstext
    else:
        outputtext = infolinktext[0:(rest_length-3)]+"..."

    rest_length -= len(outputtext)

    tweet = "#"+outputtext+" "+timespan+" "+link+" "+hashtags # Hashtag am Anfang weil der Ortsname dort ist

    try:
        status = api.PostUpdate(tweet)
    except Exception as e:
        logging.warning(str(datetime.now())+str(e))

    #print(rest_length,tweet)

    logging.info(str(datetime.now())+" "+infoID+" "+str(rest_length)+"\n\n"+tweet+"\n\n")

with open(knownfile, 'w', encoding='utf-8') as file:
    if ci > 0:
        file.write('\n'.join(titles)+'\n')
    else:
        file.write('n\n')
