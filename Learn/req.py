import requests
kv = {'user-agent':'chrome/9.0'}
url = 'https://www.smzdm.com/p/12253349/'
r = requests.get(url, headers=kv)
r.encoding = 'utf-8'
print(r.text[:3000])
