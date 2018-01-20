import errno
import os
from threading import Thread, Lock
from urllib.request import Request, urlopen
import logging
from queue import Queue
from bs4 import BeautifulSoup
import time
from psycopg2 import connect

"""
    Multi-threaded Web scraper that will collect interal profile links (filtering external links)
    for top 100 players in Overwatch and collect stats from each page. This scraper then stores 
    the data to a Postgres database to serve up to a Django website.
"""

###################################################################################################
"""
    Global Variables - completedPages is used to determine whether the page was scraped for links and images.
                     - completedLinks is used to determine whether that url was visited and stored.
                     - mutex is a global lock to make sure completedLinks is accessed safely between threads.
                     - q is a Queue object to manage worker threads
"""
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')
completedPages = []
completedLinks = []
mutex = Lock()
q = Queue()

###################################################################################################

"""
    storeToDB - Opens connection to Postgres database, convert parameters into a SQL Query then 
    commits the data. This happens with a mutex to ensure only one thread is ever writing to the
    database at a time.
                 - player(_tuple_): contains a player's battle tag and icon from Overwatch
                 - names(_list_): a list of the player's top 5 characters names
                 - icons(_list_): list of links to images for the characters
                 - stats(_tuple_): contains a player's stats, eliminations per game, and healing done per game, respectively
"""

def storeToDB(player, names, icons, stats):
    with mutex:
        conn = connect(database='owscraper', user='owsaegis', password='starkwinterglop')
        cursor = conn.cursor()
        cursor.execute("SELECT max(id) FROM top100_player")
        id_ = cursor.fetchone()[0]
        if id_ is None:
            id_ = 1
        else:
            id_ += 1
        cursor.execute("INSERT INTO top100_player VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (
            id_, player[0], player[1], names[0], icons[0], names[1], icons[1], names[2], icons[2], names[3], icons[3], names[4], icons[4], stats[0], stats[1]
        ))
        cursor.execute("SELECT * FROM top100_player")
        conn.commit()    


"""
    collectData - goes through page searching for specific user data to send to Postgres
                 - soup(_BeautifulSoup_): contains HTML file
"""

def collectData(soup):
    # Specific performance stats for a given player stored in /elminationsPerGame and healingDonePerGame
    eliminationsPerGame = ""
    healingDonePerGame = ""
    # /charIcons/ stores urls for a given player's top 5 characters and /charNames/ stores the names for top 5
    charIcons = []
    charNames = []
    # Loading /playerInfo/ with a given player's battletag
    info = soup.find_all('div', class_='player-info')
    span = info[0].find_all('span')
    playerInfo = span[1].text
    # Loading /playerIcon/ with url to icon img for a given player
    playerIconContainer = soup.find('div', class_='profile-info')
    playerIcon = playerIconContainer.find('img')['src']
    # Parsing through divs to grab elimination and healing stats for a given player
    cards = soup.find_all('div', class_='material-card')
    for card in cards:
        header = card.select('div h2')
        if 'Performance' in header[0].text:
            eliminationsPerGame = card.select('div[data-stat="EliminationsPG"]')[0].text
            healingDonePerGame = card.select('div[data-stat="HealingDonePG"]')[0].text
    # Grabs a list of divs that contain top 5 hero information 
    heroes = soup.select('div .content')[0].find_all('div', class_='material-card hero')
    for hero in heroes:
        # Parsing through content of each hero div to grab hero icon img url and hero name to store in their respective lists
        iconContainer = hero.select('div .hero-icon div')[0]['style']
        iconUrl = iconContainer.split('url(')[1].split(')')[0]
        charIcons.append(iconUrl)
        name = hero.find('h2', class_='card-title').text
        charNames.append(name)
    # Once all the data is found we send it into storeToDB to....store to the database
    storeToDB((playerInfo, playerIcon), charNames, charIcons, (eliminationsPerGame.strip(), healingDonePerGame.strip()))


"""
    collectLinks - Opens stored HTML file to scrape for internal links.
                 - directory(_string_): directory path to store HTML files
                 - domain(_string_): trimmed initial url used to ensure collected links are only internal
                 - pageName(_string_): name of page to access within /directory/
"""


def collectLinks(page, domain, pageName):
    links = []
    logging.debug('Collect Links in %s' % pageName)
    soup = BeautifulSoup(page, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        try:
            if "/profile" in href:
                if len(href.split("/")) == 5:
                    if 'update' not in href and 'mode' not in href:
                        links.append(href)
        except:
            continue
    if 'profile' in pageName:
        collectData(soup)
    with mutex:
        for link in set(links):
            if link not in completedLinks:
                logging.debug("Link added to Q: %s" % link)
                q.put(link)
        completedPages.append(pageName)
    logging.debug("Finished Link Collection")


"""
    storePage - listens for url in /q/ and grabs one when available. Opens url and stores content in memory.
              - domain(_string_): url appends to this to set as url for request 
"""


def storePage(domain):
    logging.debug("Worker Started")
    while True:
        url = q.get()  
        if url in completedLinks:
            logging.debug("Already stored %s" % url)
            q.task_done()
        else:
            logging.debug("Storing %s" % url)
            url = domain + url
            print(url)
            request = Request(url)
            completedLinks.append(url)
            request.add_header("User-Agent", "PytScrape/1.0")
            time.sleep(1)
            page = urlopen(request).read()
            # Trim link to grab name for file storage
            urlSegments = url.split(".")
            fileName = ""
            for segment in urlSegments:
                if "com" in segment:
                    fileName = segment.split("/")[1:]
                    break
            fileName = "/".join(fileName)
            collectLinks(page, domain, fileName)
            q.task_done()

if __name__ == '__main__':
    subLink = "/leaderboards/pc/global"
    domain = "https://overwatchtracker.com"
    # Thread Initializing
    print("Enter number of workers to serve up: ")
    thread_count = int(input())
    for _ in range(thread_count):
        worker = Thread(target=storePage, args=(domain,))
        worker.setDaemon(True)
        worker.start()
    print("Scraping %s for internal links and images" % domain)
    q.put(subLink)
    q.join()
