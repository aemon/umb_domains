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


domain_list = []
umbrella_url = "https://s-platform.api.opendns.com/1.0/events"
umbrella_key = "c98826cd-bd91-4e0b-9864-89b8cbfbb158"
url_post = umbrella_url+"?customerKey="+umbrella_key
print(url_post)

def CreateDomainPayload(dstDomain):
    time = datetime.now().isoformat()
    payload = {
    "alertTime": time+"Z",
    "deviceId": "ba6a59f4-e692-4724-ba36-c28132c761de",
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
        print("SUCCESS: domain list was accepted, HTTP response: 202")
    else:
        print("An error has ocurred with the following code %(error)s. Trying again in 60 sec" % {'error': req.status_code}. Trying again)
        time.sleep(60)
        PostDomainList(domain_list,url) 

def main():
    with open("fraud_phishing.txt") as file:
        for item in file:
            domain_list.append(item.strip())
    print("Number of domains", len(domain_list))
    input("Press enter:")

    domain_list_payload = []
    #Adding domains via enforcement API
    #print first 10 items
    for domain in domain_list:
        if ((domain_list.index(domain)+1) % 3000) == 0: 
            PostDomainList(domain_list_payload, url_post)
            print(domain_list.index(domain), "domains added", "waiting 60 sec")
            time.sleep(60)
            domain_list_payload = []
            continue
        domain_list_payload.append(CreateDomainPayload(domain))
    PostDomainList(domain_list_payload, url_post)
    print ("All Domains Added")

        

if __name__ == "__main__":
    main()
