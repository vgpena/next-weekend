"""
This scraper crawls OregonHikers.org for hikes, formats it as a TSV,
and then extracts useful bits of that data into a CSV.
"""

from urllib.request import Request, urlopen
from urllib.error import HTTPError
import re
import csv
import os.path
from itertools import islice

from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "http://www.oregonhikers.org"
HIKES_DB_FILENAME = "hikes_db"

class HikesSheet:
    """HikesSheet creates a CSV of hikes."""
    def __init__(self, file_name='hikes'):
        self.file_name = file_name
        self.columns = [
            'hike_name',
            'url',
            'trailhead_name',
            'trailhead_lat',
            'trailhead_lon',
            'distance',
            'time_of_year'
        ]
        self.create_headings(self.columns)

    def create_headings(self, headings_arr):
        """Creates headings in the CSV out of columns in the constructor."""
        with open("{}.csv".format(self.file_name), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headings_arr)

    def add_hike(
            self, hike_name, url, \
            trailhead_name, trailhead_lat, trailhead_lon, distance, time_of_year
        ):
        """Adds a hike with the specified fields to the CSV."""
        if not trailhead_lat or not trailhead_lon:
            print('Error adding hike to CSV: {}'.format(hike_name))
            return
        with open("{}.csv".format(self.file_name), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([
                hike_name,
                url,
                trailhead_name,
                trailhead_lat,
                trailhead_lon,
                distance,
                time_of_year
            ])

class HikesDatabase:
    """Creates a database of all hikes. Used as a sub for the live site."""
    def __init__(self, file_name=HIKES_DB_FILENAME):
        self.file_name = file_name
        self.columns = [
            'hike_url',
            'hike_html',
            'trailhead_url',
            'trailhead_html',
        ]
        self.create_headings(self.columns)

    def create_headings(self, headings_arr):
        """Creates headings in the CSV out of columns in the constructor."""
        with open("{}.tsv".format(self.file_name), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headings_arr)

    def add_hike(self, hike_name, hike_html, trailhead_name, trailhead_html):
        """Adds the name + html of a hike + trailhead to the CSV."""
        with open("{}.tsv".format(self.file_name), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([
                hike_name,
                hike_html,
                trailhead_name,
                trailhead_html,
            ])

class HikesData:
    """Used to clean/manipulate hike data before writing to a HikesSheet."""
    def __init__(self):
        self.columns = [
            'hike_name',
            'url',
            'trailhead_name',
            'trailhead_lat',
            'trailhead_lon',
            'distance',
            'time_of_year',
        ]
        self.dataframe = pd.DataFrame([], columns=self.columns)
        self.year_words = ['all', 'year', 'round', 'seasons', 'any']
        self.winter_words = ['winter', 'december', 'january', 'february']
        self.spring_words = ['spring', 'march', 'april', 'may', 'june', 'apr']
        self.summer_words = ['summer', 'june', 'july', 'august', 'september', 'jun']
        self.fall_words = ['fall', 'september', 'october', 'november', 'oct', 'nov']

        self.year_round_string = "All Year "
        self.winter_string = "Winter "
        self.spring_string = "Spring "
        self.summer_string = "Summer "
        self.fall_string = "Fall "

    def create_regex_from_list(self, regex_list):
        """Returns a regex that matches any item in a given list."""
        return re.compile(r'\b({})'.format("|".join(regex_list)))

    def add_hike(self, hike_name, url, trailhead_info, distance, time_of_year):
        """Adds a hike to the dataframe of all hikes."""
        trailhead_name, trailhead_lat, trailhead_lon = trailhead_info
        hike_dataframe = pd.DataFrame([[
            hike_name,
            url,
            trailhead_name,
            trailhead_lat,
            trailhead_lon,
            distance,
            time_of_year,
        ]], columns=self.columns)
        self.dataframe = self.dataframe.append(hike_dataframe)

    def get_season_value(
            self, raw_season, year_vals, \
            winter_vals, spring_vals, summer_vals, fall_vals
    ):
        """Gets a specific season or seasons in response to a freeform season."""
        new_time = ""
        if raw_season in year_vals:
            new_time += self.year_round_string
        if raw_season in winter_vals:
            new_time += self.winter_string
        if raw_season in spring_vals:
            new_time += self.spring_string
        if raw_season in summer_vals:
            new_time += self.summer_string
        if raw_season in fall_vals:
            new_time += self.fall_string
        if new_time:
            return new_time
        print('Season {} not in any lists of season values'.format(raw_season))
        return raw_season

    def clean_time_of_year(self):
        """
        Searches the `time_of_year` column for duplicates
        and collapses them into a canonical phrasing.
        """
        time_of_year_data = self.dataframe['time_of_year'].unique().tolist()

        year_round_regex = self.create_regex_from_list(self.year_words)
        winter_regex = self.create_regex_from_list(self.winter_words)
        spring_regex = self.create_regex_from_list(self.spring_words)
        summer_regex = self.create_regex_from_list(self.summer_words)
        fall_regex = self.create_regex_from_list(self.fall_words)

        year_round_values = [
            val for val in time_of_year_data if val and year_round_regex.search(val.lower())
        ]
        winter_values = [
            val for val in time_of_year_data if val and winter_regex.search(val.lower())
        ]
        spring_values = [
            val for val in time_of_year_data if val and spring_regex.search(val.lower())
        ]
        summer_values = [
            val for val in time_of_year_data if val and summer_regex.search(val.lower())
        ]
        fall_values = [
            val for val in time_of_year_data if val and fall_regex.search(val.lower())
        ]

        # then double back to see if any seasons were "skipped" the first time through.
        skipped_spring_values = [
            val for val in winter_values if val in summer_values and val not in spring_values
        ]
        skipped_summer_values = [
            val for val in spring_values if val in fall_values and val not in summer_values
        ]
        skipped_fall_values = [
            val for val in summer_values if val in winter_values and val not in fall_values
        ]

        # a trail is PROBABLY not open Fall-Spring without being open year-round.
        spring_values += skipped_spring_values
        summer_values += skipped_summer_values
        fall_values += skipped_fall_values

        # loop back over dataframe values to replace with canonical value of that season
        temp_dataframe = pd.DataFrame([], columns=self.columns)

        for row in self.dataframe.iterrows():
            time_of_year = self.get_season_value(
                row[1]['time_of_year'],
                year_round_values,
                winter_values,
                spring_values,
                summer_values,
                fall_values,
            )
            hike_df = pd.DataFrame([[
                row[1]['hike_name'],
                row[1]['url'],
                row[1]['trailhead_name'],
                row[1]['trailhead_lat'],
                row[1]['trailhead_lon'],
                row[1]['distance'],
                time_of_year,
            ]], columns=self.columns)
            temp_dataframe = temp_dataframe.append(hike_df)

        self.dataframe = temp_dataframe

def make_request(url):
    """Create a Request object."""
    return Request(url, headers={'User-Agent': 'Mozilla/5.0'})

def make_soup(url):
    """Reads a Request object and parses its HTML."""
    return BeautifulSoup(urlopen(make_request(url)), features="html.parser")

def make_soup_from_html(html):
    """Reads in HTML and returns a parsed bs4 tree."""
    return BeautifulSoup(html, features="html.parser")

def get_hike_name(content):
    """From bs4-parsed HTML, extract the hike name."""
    return content.find('h1').string

def get_hike_distance(content):
    """From bs4-parsed HTML, extract the hike distance."""
    try:
        return content.find('ul') \
        .find(text=re.compile(r'Distance: ')) \
        .split(': ')[1] \
        .split('\n')[0] \
        .split(' miles')[0]
    except AttributeError:
        return None

def get_hike_time_of_year(content):
    """From bs4-parsed HTML, extract the hike time of year."""
    try:
        return content.find('ul') \
        .find(text=re.compile(r'Seasons:')) \
        .split(':')[1] \
        .split('\n')[0]
    except AttributeError:
        return None

def find_all_result_pages(url, arr):
    """
    Given a base Search URL,
    hit the Next button repeatedly and return all pages findable this way.
    """

    result_pages = arr
    result_pages.append(url)

    html = make_soup(url)
    content = html.find(id='mw-content-text')
    results_counter = content.find('b')
    next_link = results_counter.next_sibling.next_sibling

    if next_link.name == 'a':
        return find_all_result_pages("{}{}".format(BASE_URL, next_link.get('href')), result_pages)

    return result_pages

def find_all_result_links(url):
    """Given a page of results, find all the links to hike pages."""
    result_pages = find_all_result_pages(url, [])
    links = []

    for result_page in result_pages:
        html = make_soup(result_page)

        wrapper = html.find_all('p')[0]
        links += wrapper.find_all('a')

    return links

def get_raw_hike_data(url):
    """Intakes a hike URL and gets the HTML for that hike and the URL + HTML for the trailhead."""
    try:
        html = make_soup(url)
    except HTTPError:
        print('Error getting hike: {}'.format(url))
        return None

    hike_html = html.find(id='mainContent')

    try:
        trailhead_url = '{}{}'.format(
            BASE_URL,
            hike_html.find('ul').find(text=re.compile(r'Start')).next_sibling.get('href')
        )
    except AttributeError:
        print('Error getting trailhead for hike: {}'.format(url))
        return None

    try:
        trailhead_html = make_soup(trailhead_url)
    except HTTPError:
        print('Error getting trailhead for hike: {}'.format(url))
        return None

    return(url, hike_html, trailhead_url, trailhead_html)

def add_hikes_to_database():
    """Scrapes the live OH.org and adds hikes to the database file."""
    db = HikesDatabase() #pylint: disable=C0103

    start_url = "http://www.oregonhikers.org/w/index.php?title=Special:Ask&limit=500&q=%5B%5BDistance%3A%3A%3E0+miles%5D%5D&p=format%3Dlist%2Flink%3Dall%2Fheaders%3Dshow%2Fsearchlabel%3D%E2%80%A6-20further-20results&sort=&order=ASC&eq=yes" #pylint: disable=C0301
    links = find_all_result_links(start_url)

    total_links = len(links)
    curr_link = 1
    for link in links:
        print('Processing {} of {}'.format(curr_link, total_links))
        data = get_raw_hike_data('{}{}'.format(BASE_URL, link.get('href')))
        curr_link += 1
        if data:
            url, html, t_url, t_html = data
            db.add_hike(url, html, t_url, t_html)

def get_trailhead_lat(content):
    """From bs4-parsed HTML, extract the trailhead lat."""
    lat = content.find(id='mw-content-text').find('ul').find(text=re.compile(r'Latitude: '))
    try:
        lat = lat.split(": ")[1].split("\n")[0]
    except AttributeError:
        print("Trailhead no lat.")
        return None
    return lat

def get_trailhead_lon(content):
    """From bs4-parsed HTML, extract the trailhead lon."""
    lon = content.find(id='mw-content-text').find('ul').find(text=re.compile(r'Longitude: '))
    try:
        lon = lon.split(": ")[1].split("\n")[0]
    except AttributeError:
        print("Trailhead no lon.")
        return None
    return lon

def get_trailhead_name(content):
    """From bs4-parsed HTML, extract the trailhead name."""
    try:
        return content.find('h1').string
    except AttributeError:
        print("Could not find trailhead name.")
        return None

def get_hike_data(row):
    """
    This function gets hike data from a row of a CSV of:
    hike URL, hike HTML, trailhead URL, trailhead HTML.
    """

    hike_url = row[0]

    hike_html = make_soup_from_html(row[1])
    hike_name = get_hike_name(hike_html)
    hike_distance = get_hike_distance(hike_html)
    hike_time_of_year = get_hike_time_of_year(hike_html)

    trailhead_html = make_soup_from_html(row[3])
    trailhead_name = get_trailhead_name(trailhead_html)
    trailhead_lat = get_trailhead_lat(trailhead_html)
    trailhead_lon = get_trailhead_lon(trailhead_html)

    return(
        hike_name,
        hike_url,
        (trailhead_name, trailhead_lat, trailhead_lon),
        hike_distance,
        hike_time_of_year
    )

def scrape():
    """
    Scrape OregonHikers starting from a results page
    and create a CSV of hike info found that way.
    """

    if not os.path.isfile('{}.tsv'.format(HIKES_DB_FILENAME)):
        # if a local copy doesn't already exist,
        # create it, populate it, and then run the whole program again.
        print('Local copy of data does not exist. Downloading...')
        add_hikes_to_database()
        print('Done adding hike to database!')

    with open("{}.tsv".format(HIKES_DB_FILENAME), 'r', newline='') as file:
        reader = csv.reader(file, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        total_hikes = sum(1 for row in reader) - 1
        file.seek(0)

        data_frame = HikesData()

        curr_row = 1
        for row in islice(reader, 1, None):
            print('Adding hike {} / {}'.format(curr_row, total_hikes))
            curr_row += 1
            hike_data = get_hike_data(row)
            hike_name, url, trailhead_info, distance, time_of_year = hike_data
            data_frame.add_hike(hike_name, url, trailhead_info, distance, time_of_year)
        data_frame.clean_time_of_year()

        sheet = HikesSheet()
        for row in data_frame.dataframe.iterrows():
            hike_name, url, trailhead_name, \
            trailhead_lat, trailhead_lon, distance, time_of_year = row[1]
            sheet.add_hike(
                hike_name, url, \
                trailhead_name, trailhead_lat, trailhead_lon, distance, time_of_year
            )

        print('Done!')
        exit(1)

scrape()
