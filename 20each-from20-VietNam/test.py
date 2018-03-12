# server 54.191.208.174

from __future__ import print_function
import hashlib
import requests
import json

def getPageInfo(title, limit, offset):
    url = "https://vi.wikipedia.org/w/api.php?action=query&format=json&prop=links&titles=" + title + "&utf8=1&plnamespace=0|6|14|108|446&pllimit=" + str(limit + offset)
    res = requests.get(url)
    resj = json.loads(res.text)
    pages = resj['query']['pages']
    pageID = list(pages.keys())[0]
    pageTitle = pages[pageID]['title']
    links = None
    if pageID == '-1':
        m = hashlib.md5()
        m.update(pageTitle.encode('utf-8'))
        # print(pageTitle.encode('utf-8'))
        pageID = m.hexdigest()
    elif "links" in pages[pageID]:
        links = pages[pageID]['links'][offset:]
    return (pageID, pageTitle, links)

def loadData(level, id2title, adjList, baseTitles):
    with open(str(level) + 'level-id2title.txt', 'r') as f:
        for line in f.readlines():
            pageID, pageTitle = line.rstrip().split("\t")
            id2title[pageID] = pageTitle

    with open(str(level) + 'level-adjList2.txt', 'r') as f:
        for line in f.readlines():
            pageIDs = line.rstrip().split(" ")
            if len(pageIDs) == 1:
                adjList[pageIDs[0]] = []
            else: 
                adjList[pageIDs[0]] = pageIDs[1:]
            # print(pageIDs)

    with open(str(level) + 'level-nextBaseTitles.txt', 'r') as f:
        for line in f.readlines():
            arr = line.rstrip().split("\t")
            title = arr[0]
            baseTitles[title] = arr[1:]
            # print(arr[1:])

def save(level, id2title, adjList, baseTitles):            
    with open(str(level) + 'level-id2title.txt', 'w') as f:
        for _id in id2title:
            f.write(_id + "\t" + id2title[_id])
            f.write("\n")

    with open(str(level) + 'level-adjList.txt', 'w') as f:
        for _id in adjList:
            if len(adjList[_id]):
                for nextId in adjList[_id]:
                    f.write(_id + " " + nextId + "\n")

    with open(str(level) + 'level-adjList2.txt', 'w') as f:
        for _id in adjList:
            f.write(_id)
            for nextId in adjList[_id]:
                f.write(" " + nextId)
            f.write("\n")

    with open(str(level) + 'level-nextBaseTitles.txt', 'w') as f:
        for title in baseTitles:
            f.write(title)
            for parentId in baseTitles[title]:
                f.write("\t" + parentId)
            f.write("\n")

def graphOpening(baseTitles, level, limit, offset, adjList, id2title):
    """
    Start with a baseTitles
    1) for each title in baseTitles:
        1.1) get pageID, links
        1.2) add pageID to id2title:
            1.2.1: if pageID exist: don't add it to nextLevelTitles, isInspected = True
            1.2.2: if not: add it to id2title
        1.3) add pageID to adjList:
            1.3.1) add pageID to adjList of its parents (baseTitles[title])
            1.3.1) if pageID not exist in adjList: init adjList for pageID
        1.4) if links: add links to nextLevelTitles:
            1.4.1) if title exist in nextLevelTitles: add pageID to title's parent
            1.4.2) if not: add to nextLevelTitles
        
    """
    nextLevelTitles = {} # each element: {"title": <title>, "parent": [<parentID>]}
    while level >= 0:
        for title in baseTitles:
            isInspected = False
            print(title + "-", end="")
            pageID, pageTitle, links = getPageInfo(title, limit, offset)
            print(pageID + "--")
            # add mapping info
            if pageID not in id2title:
                id2title[pageID] = pageTitle
            else:
                isInspected = True
                print("\ninspected page")
            # init adjacency list for pageID
            if pageID not in adjList:
                adjList[pageID] = []
            # add to adjecency list of it's parents
            preds = baseTitles[title]
            for pred in preds:
                if pageID not in adjList[pred]:
                    adjList[pred].append(pageID)
            # find next level pages
            if links and (not isInspected):
                for item in links:
                    title = item['title']
                    if title in nextLevelTitles:
                        nextLevelTitles[title].append(pageID) # don't need to check
                    else:
                        nextLevelTitles[title] = [pageID]

        level -= 1
        baseTitles = nextLevelTitles
        nextLevelTitles = {}
    return baseTitles

            
id2title = {}
adjList = {}

limit = 20
offset = 20
odlLevel = 0
level = 1
if odlLevel == 0:
    baseTitles = {"Việt Nam": []}
else:
    baseTitles = {}
    loadData(odlLevel, id2title, adjList, baseTitles)

baseTitles = graphOpening(baseTitles, level - odlLevel, limit, offset, adjList, id2title)
save(level, id2title, adjList, baseTitles)
