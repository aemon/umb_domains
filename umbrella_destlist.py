import requests
import socket
import configparser
import json
import sys
from pathlib import Path
from requests.packages.urllib3.exceptions import InsecureRequestWarning

def GetUmbrellaToken(auth_url, api_key, api_secret):
    payload = None
    headers = {
        "Content-type" : "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    req = requests.post(auth_url,headers=headers,auth=(api_key, api_secret))
    resp = json.loads(req.text)
    return resp["access_token"]

def CreateDestGroup(umb_token, list_name):
    url = 'https://api.umbrella.com/policies/v2/destinationlists'
    headers = { 
        "Authorization": "Bearer "+umb_token,
        "Content-type": "application/json" 
    }
    payload = None
    req = requests.get(url, headers=headers, data=payload)
    resp = json.loads(req.text)
    #Check if list is already exists and get it's id"
    for list_data in resp["data"]:
        if list_data['name'] == list_name:
            list_id = list_data['id']
            return list_id

    #Create a new list with group name
    payload = json.dumps({
        "access": "allow",
        "isGlobal": False,
        "name": list_name
    })
    #response = requests.request("POST", url, headers=headers, data=payload)
    req = requests.post(url, headers=headers, data=payload)
    return req.json()['id']


def AddDomaintoList(list_id, umb_domain_list,umb_token):
    payload = json.dumps(umb_domain_list)
    headers = { 
        "Authorization": "Bearer "+umb_token,
        "Content-type": "application/json" 
    }
    url = 'https://api.umbrella.com/policies/v2/destinationlists/'+str(list_id)+'/destinations'
    req = requests.post(url, headers=headers, data=payload)
    print("Status Code:", req.status_code)

domain_list = []
umbrella_auth_url = "https://api.umbrella.com/auth/v2/token"
umbrella_api_url = "https://api.umbrella.com"
umb_api_key = "bbe87ac8df2f4d2ea90957cc0b23b9cc"
umb_api_secret = "feb48342f2864387b7fd764f91b78219"

def main():
    with open("fraud_phishing.txt") as file:
        for item in file:
            domain_list.append(item.strip())
    print("Number of domains", len(domain_list))
    #input("Press enter:")
    umb_token = GetUmbrellaToken(umbrella_auth_url,umb_api_key,umb_api_secret)
    list_id = CreateDestGroup(umb_token,"NBU Phishing List")
    print("List ID:", list_id)
    umb_domain_list = []
    #Add 1000 first domains to a list
    added_domains = 0
    for domain in domain_list:
        umb_domain = {}
        umb_domain["destination"] = domain
        umb_domain["comment"] = "NBU Phishing Domain"
        umb_domain_list.append(umb_domain)
        if len(umb_domain_list) == 500:
            AddDomaintoList(list_id,umb_domain_list,umb_token)
            umb_domain_list = []
            added_domains += 500
            print('Domains added:', added_domains)
    AddDomaintoList(list_id,umb_domain_list,umb_token)
    added_domains += len(umb_domain_list)
    print('Domains added:', added_domains)

if __name__ == "__main__":
    main()
