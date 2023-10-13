# Samyukta Iyengar (siyengar)

import sys

def readCrawlerFile(crawlerOutputFile):
    with open(crawlerOutputFile, "r") as f:
        URLs = f.read().splitlines()
    return URLs

def readLinksFile(linksOutputFile):
    with open(linksOutputFile, "r") as f:
        links = f.read().splitlines()
    return links

def getAdjList(inputURLs, inputLinks):
    adjLists = {u: [] for u in inputURLs}
    for link in inputLinks:
        s, d = link.split(" ", 1)
        if s in inputURLs and d in inputURLs:
            adjLists[s].append(d)
    return adjLists

def pagerank(convergenceThreshold, inputURLs, inputLinks, inputScores, adjList):
    converged = False
    count = 0
    while not converged:
        scores2 = {}
        for u in inputURLs:
            links = adjList[u]
            countOutgoingLinks = len(links)
            for link in links:
                scores2[link] = 0.15 + (0.85 * inputScores[u] / countOutgoingLinks)
        for u in inputURLs:
            if u not in scores2:
                scores2[u] = 0.15
        converged = all(abs(scores2[u] - inputScores[u]) < convergenceThreshold for u in inputURLs)
        inputScores = scores2
        count += 1
    return inputScores, count
    
def writeOutput(inputScores):
    with open('pagerank.output', 'w') as f:
        for u, s in sorted(inputScores.items(), key = lambda x: x[1], reverse = True):
            f.write(u + ' ' + str(s) + '\n')

if __name__ == "__main__":
    crawlerOutputFile = sys.argv[1]
    linksOutputFile = sys.argv[2]
    convergenceThreshold = float(sys.argv[3])
    URLs = readCrawlerFile(crawlerOutputFile)
    links = readLinksFile(linksOutputFile)
    scores = {u: 0.25 for u in URLs}
    adjList = getAdjList(URLs, links)
    scores, numberOfIterations = pagerank(convergenceThreshold, URLs, links, scores, adjList)
    writeOutput(scores)
    print(numberOfIterations)