from datetime import datetime
import time
import requests
import socket
import configparser
import json
import sys
from pathlib import Path
#import webexteamssdk
#from crayons import blue, green, red
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm


domain_list = []
umbrella_url = "https://s-platform.api.opendns.com/1.0/events"
umbrella_key = "d3891991-2fb9-4892-a2a1-66a2ee70f91d"
url_post = umbrella_url+"?customerKey="+umbrella_key
print(url_post)

def CreateDomainPayload(dstDomain):
    time = datetime.now().isoformat()
    payload = {
    "alertTime": time+"Z",
    "deviceId": "d3891991-2fb9-4892-a2a1-66a2ee70f91d",
    "deviceVersion": "13.7a",
    "dstDomain": dstDomain,
    "dstUrl": "http://"+dstDomain+"/",
    "eventTime": time+"Z",
    "protocolVersion": "1.0a",
    "providerName": "Security Platform"
    }
    headers = {'Content-type': 'application/json'}
    return payload


def PostDomainList(domain_list, url):
    headers = {'Content-type': 'application/json'}
    req = requests.post(url_post, headers=headers, data=json.dumps(domain_list))
    # error handling if true then the request was HTTP 202, so successful
    if(req.status_code == 202):
        tqdm.write("\n SUCCESS: domain list was accepted, HTTP response: 202")
    else:
        print("An error has occurred with the following code %(error)s. Trying again in 60 sec" % {'error': req.status_code} )
        time.sleep(60)
        PostDomainList(domain_list,url) 

def GetPhishingList():
    new_list = requests.get('https://fmisp.ncscc.gov.ua/feed/fraud_phishing.txt')


def main():
    old_list = []
    new_list = []

    with open("fraud_phishing_old.txt") as file:
        for item in file:
            old_list.append(item.strip())
    print("Number of domains in old list", len(old_list))

    with open("fraud_phishing_new.txt") as file:
        for item in file:
            new_list.append(item.strip())
    print("Number of domains in new list", len(new_list))


    domain_list = list(set(new_list) - set(old_list))

    print("Number of domains", len(domain_list))
    input("Press enter:")

    domain_list_payload = []
    #Adding domains via enforcement API
    #print first 10 items
    for domain in tqdm(domain_list, ncols=100, ascii=True, desc='Total progress'):
        if ((domain_list.index(domain)+1) % 30) == 0:
            PostDomainList(domain_list_payload, url_post)
            #print(domain_list.index(domain), "domains added, waiting for 60 sec")
            tqdm.write(str(domain_list.index(domain)) + " domains added \n")
            time.sleep(6)
            domain_list_payload = []
            continue
        domain_list_payload.append(CreateDomainPayload(domain))
        tqdm.write(domain)
    PostDomainList(domain_list_payload, url_post)
    tqdm.write ("All Domains Added")

if __name__ == "__main__":
    main()
