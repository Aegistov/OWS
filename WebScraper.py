import errno
import os
from threading import Thread, Lock
import urllib2
import logging
from Queue import Queue
import time

"""
    Multi-threaded Web scraper that will collect internal links (filtering external links) and download images on each
    page. This scraper will setup a directory to store HTML content of a given page and a sub-directory for all down-
    loaded images.
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
    collectLinks - Opens stored HTML file to scrape for internal links.
                 - directory(_string_): directory path to store HTML files
                 - domain(_string_): trimmed initial url used to ensure collected links are only internal
                 - pageName(_string_): name of page to access within /directory/
"""


def collectLinks(dir, domain, pageName):
    links = []
    logging.debug('Collect Links in %s' % pageName)
    if pageName in completedPages:
        return
    # Open specified file and search line by line for a url
    with open("/".join([dir, pageName]), "r") as dom:
        for line in dom:
            if line.find("<a") > 0:
                href = line.find("href=")
                if href > 0:
                    subString = line[href + 5:]
                    start = subString.find("\"")
                    end = subString.find("\"", start + 1)
                    # /subString/ is a discovered url and must match /domain/ before being appended to avoid
                    # collecting external urls
                    if subString.find(domain) > 0:
                        links.append(subString[start + 1:end])
    with mutex:
        for link in set(links):
            if link not in completedLinks:
                logging.debug("Link added to Q: %s" % link)
                q.put(link)
        completedPages.append(pageName)
    logging.debug("Finished Link Collection")


"""
    storePage - listens for url in /q/ and grabs one when available. Opens url and stores content in /directory/ path.
              - dir(_string_): directory path to store HTML files
"""


def storePage(dir):
    logging.debug("Worker Started")
    while True:
        url = q.get()
        if url in completedLinks:
            logging.debug("Already stored %s" % url)
            q.task_done()
        else:
            logging.debug("Storing %s" % url)
            completedLinks.append(url)
            page = urllib2.urlopen(url)
            # Trim link to grab name for file storage
            link = url.split(".")
            sub = link[2].split("/")
            if len(sub) < 2 or (len(sub) == 2 and sub[1] == ''):
                fileName = 'home'
            else:
                fileName = sub[1]
            # File storage
            file_ = open(dir + "/" + fileName, "w")
            file_.write(page.read())
            file_.close()
            # Launch scraping
            collectLinks(dir, domain, fileName)
            q.task_done()


def directoryStatus(dir):
    print("Determining Directory Status...")
    try:
        os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return True


if __name__ == '__main__':
    # Setting up Directory
    directory = os.path.dirname("webpage/")
    if directoryStatus(directory):
        print("Directory exists")
    print("Enter URL of website to scrape: ")
    site = str(input())
    # Domain Extraction -- trims http, www, etc. prefixes and .* postfixes (/, /inventory, etc.)
    domain = site.split(".")
    domain = ".".join([domain[-2].split("/")[-1], domain[-1].split("/")[0]])
    # Thread Initializing
    print("Enter number of workers to serve up: ")
    thread_count = int(input())
    for _ in range(thread_count):
        worker = Thread(target=storePage, args=(directory,))
        worker.setDaemon(True)
        worker.start()
    print("Scraping %s for internal links and images" % domain)
    q.put(site)
    q.join()
