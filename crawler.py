# Samyukta Iyengar (siyengar)

import os
import ssl
import sys
import threading
import urllib.request
from collections import defaultdict
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse

FILE_EXTENSIONS = ['mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif', 'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg', 'cdr', 'ico', 'pdf']

# Parser class
class Parser(HTMLParser):
    def __init__(self, URL):
        super().__init__()
        self.URL = URL
        self.links = defaultdict(set)
        self.reset()
        if os.path.splitext(self.URL)[-1][1:] in FILE_EXTENSIONS:
            return
        URLRequest = []
        headers = {'User-Agent':'Chrome/50.0.2661.102'}
        req = urllib.request.Request(url = self.URL, headers = headers)
        if self.URL.startswith("https"):
            scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            URLRequest = urllib.request.urlopen(req, context = scontext, timeout = 10)
        else:
            scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            req = urllib.request.Request(url = self.URL, headers = headers)
            URLRequest = urllib.request.urlopen(req, context = scontext, timeout = 10)
        html = URLRequest.read().decode()
        URLRequest.close()
        super().feed(html)
    
    def handle_starttag(self, tag, attrs):
        if tag == "a":
           for name, link in attrs:
               if name == "href":
                    if (link.startswith("http") or link.startswith("https")):
                        self.links.setdefault(self.URL, set()).add(link.rstrip('/'))
                    else:
                        newURL = urllib.parse.urljoin(self.URL, link).rstrip('/')
                        if isURL(newURL):
                            self.links.setdefault(self.URL, set()).add(newURL)

# Crawler class
class Crawler:
    def __init__(self, seedURL, maxURLs):
        self.seedURL = seedURL.rstrip('/')
        self.maxURLs = maxURLs
        self.links = defaultdict(set)
        self.totalLinks = 0
        self.seenURLs = set()
        self.visitedURLs = []
        self.queue = deque([])
        self.queue.append(self.seedURL)
        self.seenURLs.add(self.seedURL)
        sys.setrecursionlimit(10**7)
        threading.stack_size(2**27)

    def crawl(self, URL):
        while len(self.queue) > 0:
            if len(self.visitedURLs) >= self.maxURLs:
                break
            currentURL = self.queue.popleft()
            currentURL2 = currentURL
            currentURL2 = currentURL2.replace('http://', '')
            currentURL2 = currentURL2.replace('https://', '')
            self.visitedURLs.append(currentURL2)
            try:
                parser = Parser(currentURL)
                for u, links in parser.links.items():
                    for link in links: 
                        if link.startswith('javascript'):
                            continue
                        if os.path.splitext(link)[-1][1:] in FILE_EXTENSIONS:
                            continue
                        currentURL2 = link
                        currentURL2 = currentURL2.replace('http://', '')
                        currentURL2 = currentURL2.replace('https://', '')
                        flag = False
                        for i in self.queue:
                            if i == link:
                                flag = True
                                break
                        if flag == False:
                            if (self.visitedURLs.count(currentURL2)) == 0:
                                self.seenURLs.add(link)
                                self.queue.append(link)
                                if self.totalLinks < self.maxURLs:
                                    self.totalLinks += 1
                                    self.links.setdefault(u, set()).add(link)
            except Exception as e:
                print(e)
                print("Error: failed to retrieve url")
                print(URL)
    
    def getAllURLs(self):
        return self.seenURLs
    
    def getVisitedURLs(self):
        return self.visitedURLs
    
    def getLinks(self):
        return self.links

# Helper functions

def isURL(inputURL):
    try:
        result = urlparse(inputURL)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
def getSeedURL(seedURLFile):
    file = open(seedURLFile, "r")
    URLs = [line.rstrip('\n') for line in file]
    file.close()
    return URLs

def writeOutput(outputFile, crawler):
    allURLs = crawler.getAllURLs()
    file = open(outputFile, "w")
    for u in allURLs:
        file.write("%s\n" % (u))
    file.close()

def writeLinks(linksFile, crawler):
    links = crawler.getLinks()
    file = open(linksFile, "w")
    for u, links in links.items():
        for link in links:
            file.write("%s %s\n" % (u, link))
    file.close()

# main
if __name__ == "__main__":
    seedURLFile = sys.argv[1]
    maxURLs = int(sys.argv[2])
    URLs = getSeedURL(seedURLFile)
    for u in URLs: 
        crawler = Crawler(u, maxURLs)
        crawler.crawl(u)
        writeOutput("crawler.output", crawler)
        writeLinks("links.output", crawler)