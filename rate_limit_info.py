import requests, json
from time import sleep
from datetime import datetime as dt

def getRateLimit(auth):
    r = requests.get('https://api.github.com/rate_limit', auth=auth)
    res = r.json()['rate']
    return res

def loadConfig(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
        authList = [(name, key) for name, key in config['github.auth']]
    return config, authList

remain = 0
tf = "%Y-%m-%dT%H:%M:%SZ"

config, authList = loadConfig('settings.json')
for auth in authList:
    res = getRateLimit(auth)
    remain += res['remaining']
    print(auth[0], res)
    reset_time = dt.fromtimestamp(res['reset'])
    t = (reset_time-dt.now())        
    print(f"Reset time: {reset_time.strftime('%c')}, {t.total_seconds()} seconds remaining.")