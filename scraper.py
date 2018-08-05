from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import re
import csv
import pdb


baseURL = "http://www.oregonhikers.org"

class HikesSheet:
    def __init__(self, file_name='hikes'):
        self.file_name = file_name
        self.columns = ['hike_name', 'url', 'trailhead_name', 'trailhead_lat', 'trailhead_lon', 'distance', 'time_of_year']
        self.createHeadings(self.columns)

    def createHeadings(self, headingsArr):
        with open("{}.csv".format(self.file_name), 'w', newline='') as csvfile:
            writer =  csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headingsArr)

    def addHike(self, hike_name, url, trailhead_info, distance, time_of_year):
        trailhead_name, trailhead_lat, trailhead_lon = trailhead_info
        with open("{}.csv".format(self.file_name), 'a', newline='') as csvfile:
            writer =  csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([hike_name, url, trailhead_name, trailhead_lat, trailhead_lon, distance, time_of_year])



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
    try:
        distance = content.find('ul').find(text=re.compile(r'Distance: ')).split(': ')[1].split('\n')[0].split(' miles')[0]
    except:
        return None
    
    try:
        time_of_year = content.find('ul').find(text=re.compile(r'Seasons: ')).split(': ')[1].split('\n')[0]
    except:
        return None

    # TODO: Forest pass/fees; dogs y/n

    return (hike_name, url, trailhead_info, distance, time_of_year)

def scrape():
    # TODO: loop over all pages of results
    startURL = "http://www.oregonhikers.org/w/index.php?title=Special:Ask&limit=500&q=%5B%5BDistance%3A%3A%3E0+miles%5D%5D&p=format%3Dlist%2Flink%3Dall%2Fheaders%3Dshow%2Fsearchlabel%3D%E2%80%A6-20further-20results&sort=&order=ASC&eq=yes"

    html = makeSoup(startURL)

    wrapper = html.find_all('p')[0]
    links = wrapper.find_all('a')

    sheet = HikesSheet()

    totalHikes = 0
    for link in links:
        data = crawlPage("{}{}".format(baseURL, link.get('href')))
        if not data:
            continue
        hike_name, url, trailhead_info, distance, time_of_year = data
        sheet.addHike(hike_name, url, trailhead_info, distance, time_of_year)
        totalHikes+=1
    print('Done! {} hikes added.'.format(totalHikes))
    exit(1)

scrape()