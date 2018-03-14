# server 54.191.208.174

from __future__ import print_function
import hashlib
import requests
import json
import argparse
import os

def getPageInfo(title, limit, offset):
    url = "https://vi.wikipedia.org/w/api.php?action=query&format=json&prop=links&titles=" + title + "&utf8=1&plnamespace=0|6|14|108|446&pllimit=" + str(limit + offset)
    # print(url)
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

def save(source_folder, num_pages, id2title, adjList):   
    if not os.path.exists(source_folder):
        os.mkdir(source_folder)
        
    with open(os.path.join(source_folder, str(num_pages) + 'vertex-id2title.txt'), 'w') as f:
        for _id in id2title:
            f.write(_id + "\t" + id2title[_id])
            f.write("\n")

    with open(os.path.join(source_folder, str(num_pages) + 'vertex-adjList.txt'), 'w') as f:
        for _id in adjList:
            if len(adjList[_id]):
                for nextId in adjList[_id]:
                    f.write(_id + " " + nextId + "\n")

    with open(os.path.join(source_folder, str(num_pages) + 'vertex-adjList2.txt'), 'w') as f:
        for _id in adjList:
            f.write(_id)
            for nextId in adjList[_id]:
                f.write(" " + nextId)
            f.write("\n")

def graphOpening(maxNumPage = 0, baseTitles = None, limit = 0, offset = 0, adjList = None, id2title = None, source_folder = None):
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
    stop = False
    while True:
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
            # add to adjacency list of it's parents
            preds = baseTitles[title]
            for pred in preds:
                if pageID not in adjList[pred]:
                    adjList[pred].append(pageID)
            # backup
            if not isInspected and (len(id2title) % 5000 == 0):
                save(source_folder, len(id2title), id2title, adjList)
            # find next level pages
            if links and (not isInspected) and (not stop):
                for item in links:
                    title = item['title']
                    if title in nextLevelTitles:
                        nextLevelTitles[title].append(pageID) # don't need to check
                    else:
                        nextLevelTitles[title] = [pageID]
        if stop or len(nextLevelTitles) == 0:
            print("STOP")
            break
        if len(id2title) + len(nextLevelTitles) > maxNumPage:
            print("pre STOP")
            stop = True
            baseTitles = {}
            num_more = maxNumPage - len(id2title)
            for item in nextLevelTitles.items():
                if num_more: 
                    num_more -= 1
                    baseTitles.update({item[0]: item[1]})
                else: break
        else:
            baseTitles = nextLevelTitles

        nextLevelTitles = {}
            
    save(source_folder, len(id2title), id2title, adjList)

def main(startPage, maxNumPage, limit, offset):
    source_folder = "{}each-from{}-{}".format(limit, offset, startPage)
    id2title = {}
    adjList = {}
    baseTitles = {}
    baseTitles[startPage] = []

    graphOpening(maxNumPage= maxNumPage, baseTitles = baseTitles, limit = limit, offset = offset, adjList = adjList, id2title = id2title, source_folder= source_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="crawl data from wiki, start at a specific page")
    parser.add_argument('--startPage', type=str, help="title of particular page to start opening graph")
    parser.add_argument('--limit', type=int, help = "limit number of retrieval links for each page")
    parser.add_argument('--offset', type=int, help ="not open graph to <offset> first links for each page")
    parser.add_argument('--maxNumPage', type=int, help ="maximum number of pages want to get")
    args = vars(parser.parse_args())
    main(args['startPage'], args['maxNumPage'], args['limit'], args['offset'])
