from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

import pdb

def makeRequest(url):
    return Request(url, headers={'User-Agent': 'Mozilla/5.0'})

def crawl_page(url):
    print(url)

def scrape():
    # TODO: loop over all pages of results
    startURL = "http://www.oregonhikers.org/w/index.php?title=Special:Ask&limit=500&q=%5B%5BDistance%3A%3A%3E0+miles%5D%5D&p=format%3Dlist%2Flink%3Dall%2Fheaders%3Dshow%2Fsearchlabel%3D%E2%80%A6-20further-20results&sort=&order=ASC&eq=yes"
    baseURL = "http://www.oregonhikers.org"

    request = makeRequest(startURL)
    page = urlopen(request)

    html = BeautifulSoup(page)

    wrapper = html.find_all('p')[0]
    links = wrapper.find_all('a')

    for link in links:
        crawl_page("{}{}".format(baseURL, link.get('href')))

scrape()