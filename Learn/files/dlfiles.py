import re
import requests
import threading
import gevent
from gevent import pool


with open('urls_sexy.txt', 'r') as files:
    urls = files.readlines()
for i in range(0, len(urls)):
    urls[i] = urls[i].rstrip('\n')

def download_pic(url):
    link = url
    headers = {'User-Agent': 'Mozilla/5.0'}
    filename = re.search(r'[^\/]+$', link).group(0)
    try:
        r = requests.get(link, headers=headers, timeout=20)
        with open('C:/codes/Learn/files/temp/' + filename, "wb") as f:
            f.write(r.content)
        f.close()
    except Exception as e:
        print(e)

# for link in urls[100:105]:
# link = 'http://i.imgur.com/2cgInEG.jpg'
p = pool.Pool(10)
threads = [p.spawn(download_pic, link) for link in urls]
gevent.joinall(threads)