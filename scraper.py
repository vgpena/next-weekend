from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

def scrape():
    startURL = "http://www.oregonhikers.org/w/index.php?title=Special:Ask&limit=500&q=%5B%5BDistance%3A%3A%3E0+miles%5D%5D&p=format%3Dlist%2Flink%3Dall%2Fheaders%3Dshow%2Fsearchlabel%3D%E2%80%A6-20further-20results&sort=&order=ASC&eq=yes"

    request = Request(startURL, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(request)

    print(BeautifulSoup(page))

scrape()