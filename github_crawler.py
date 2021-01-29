import pymongo
import sys, json, traceback
import requests
from time import sleep
from datetime import datetime as dt
import csv

def loadConfig(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
        authList = [(name, key) for name, key in config['github.auth']]
    return config, authList

def getMongoClient(config):
    host = config['mongodb.auth']['host']
    port = int(config['mongodb.auth']['port'])
    mongo = pymongo.MongoClient(host=host, port=port)
    return mongo

def getRateLimit(auth):
    r = requests.get('https://api.github.com/rate_limit', auth=auth)
    res = r.json()['rate']
    return res

def getSleepSec(t):
    sleep_sec = (dt.fromtimestamp(t)-dt.now()).total_seconds()
    return sleep_sec

def getAvailableAuth(authList):
    rates = [{'auth':auth, 'rate':getRateLimit(auth)} for auth in authList]    
    rates.sort(key=lambda x : x['rate']['reset'])
    for x in rates:
        sleep_sec = getSleepSec(x['rate']['reset'])
        if x['rate']['remaining'] > 0 or sleep_sec < 0:
            return x['auth'], 0
    sleep_sec = getSleepSec(rates[0]['rate']['reset'])
    return rates[0]['auth'], sleep_sec

def printLog(msg):
    t = dt.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{t}] {msg}")

#Crawling + Storing
def loadRepositories(fname):
    with open(fname, 'r') as f:
        repos = csv.reader(f)
        repos = [(name, repo, status) for name, repo, status in repos]
    return repos

def handleReqException(r, authList):
    # Handling exceptions. Sleep when rate limit exceeded.
    if r.status_code == 404 or r.status_code == 451:
        printLog("Error (%d) - %s " % (r.status_code, r.json()['message']))
        return 'break'
    elif r.status_code == 403:
        j = r.json()
        if 'message' in j and 'limit' in j['message']:
            auth, sleep_sec = getAvailableAuth(authList)
            if sleep_sec > 0:
                printLog(f"Limit exceeded. Sleeping {sleep_sec} seconds.")
                sleep(sleep_sec)
            else:
                printLog(f"Trying alternate credential - {auth[0]}")
            return 'continue', auth, sleep_sec
    return 'break'

def parseResponse(response, issues, repo_id):
    for res in response:
        issue = {
            "repo_id": repo_id,
            "id": res['id'],
            "issue_number": res['number'],
            "user_id": res['user']['login'] if 'user' in res else '',
            "title": res['title'],
            "state": res['state'],
            "created_at": res['created_at'],
            "closed_at": res['closed_at']
        }
        issues.append(issue)

def storeData(issues, mongo):
    mongo['github'].issues.insert_many(issues)

def getURL(repo_id):
    return f"https://api.github.com/repos/{repo_id}/issues"

def main(argv):    
    config_file = "settings.json" if len(argv) < 2 else argv[2]
    printLog(f"Running with {config_file}")
    config, authList = loadConfig(config_file)
    if config is None or authList is None:
        printLog("Cannot load configuration.")
        exit(1)
    print(authList)

    mongo = getMongoClient(config)
    repos = loadRepositories(config['repo_file'])
    try:        
        for i in range(len(repos)):
            owner, repo, status = repos[i]
            if status == 'done':
                continue 
            printLog(f"Collecting issues for {repo}")
            auth, sleep_sec = getAvailableAuth(authList)
            repo_id = f"{owner}/{repo}"
            url = getURL(repo_id)            

            # Collect all issues.
            params = {"page": 1, "per_page": config['per_page']}
            issues = []            
            while True:
                r = requests.get(url, params=params, auth=auth)
                try:
                    r.raise_for_status()
                    response = r.json()
                except:
                    cmd, auth, sleep_sec = handleReqException(r, authList)
                    if cmd == 'break':
                        break
                    elif cmd == 'continue':
                        continue
                parseResponse(response, issues, repo_id)
                if len(response) < config['per_page']:
                    break

                params['page'] += 1
            storeData(issues, mongo)
            repos[i] = (owner, repo, 'done') # Mark finished project.
    except Exception:
        printLog("Error occurred while collecting data.")
        traceback.print_exc()            
    finally:
        with open(config['repo_file'], 'w', newline='') as f:
            out = csv.writer(f)
            out.writerows(repos)
            
    mongo.close()

if __name__ == "__main__":
    main(sys.argv)