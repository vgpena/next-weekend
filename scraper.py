from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import re

import pdb


baseURL = "http://www.oregonhikers.org"

def makeRequest(url):
    return Request(url, headers={'User-Agent': 'Mozilla/5.0'})

def makeSoup(url):
    return BeautifulSoup(urlopen(makeRequest(url)), features="html.parser")

def getTrailheadInfo(content):
    link = content.find('ul').find('li').find('a')
    if link is None:
        return None

    url = link.get('href')

    try:
        html = makeSoup("{}{}".format(baseURL, url))
    except HTTPError:
        print("Trailhead 404: {}{}".format(baseURL, url))
        return None

    data = html.find(id='mw-content-text').find('ul')

    lat = data.find(text=re.compile(r'Latitude: '))
    lon = data.find(text=re.compile(r'Longitude: '))

    if not lat or not lon:
        return None

    try:
        lat = lat.split(": ")[1].split("\n")[0]
    except:
        print("Trailhead no lat: {}{}".format(baseURL, url))
        return None

    try:
        lon = lon.split(": ")[1].split("\n")[0]
    except:
        print("Trailhead no lon: {}{}".format(baseURL, url))
        return None

    name = html.find('h1').string

    return((name, lat, lon))


def crawlPage(url):
    html = makeSoup(url)
    content = html.find(id='mainContent')
    # get trailhead data
    trailhead_info = getTrailheadInfo(content)
    # some trailheads 404. In this case, don't bother listing the hike.
    if trailhead_info is None:
        return

    # continue getting hike data
    hike_name = content.find('h1').string

    print(hike_name)

def scrape():
    # TODO: loop over all pages of results
    startURL = "http://www.oregonhikers.org/w/index.php?title=Special:Ask&limit=500&q=%5B%5BDistance%3A%3A%3E0+miles%5D%5D&p=format%3Dlist%2Flink%3Dall%2Fheaders%3Dshow%2Fsearchlabel%3D%E2%80%A6-20further-20results&sort=&order=ASC&eq=yes"

    html = makeSoup(startURL)

    wrapper = html.find_all('p')[0]
    links = wrapper.find_all('a')

    for link in links:
        crawlPage("{}{}".format(baseURL, link.get('href')))

scrape()