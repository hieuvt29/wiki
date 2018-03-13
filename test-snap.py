from __future__ import print_function, unicode_literals
import networkx as nx
import matplotlib.pyplot as plt
from mayavi import mlab
import sys, os
reload(sys)
sys.setdefaultencoding("ISO-8859-1")
mlab.options.offscreen = True
from operator import itemgetter
import argparse

def plotGraph(g, id2title, source_folder):
    pos = nx.spring_layout(g)
    plt.axis('off')
    nx.draw_networkx(g, pos, dim=2, labels=id2title, font_size=7, font_color= "green", alpha = 0.7, node_size=20, linewidths=0.1, line_color='lightyellow')
    plt.savefig(os.path.join(source_folder, 'net.png'))
    plt.show()

def run_pagerank(g):
    pr = nx.pagerank(g, alpha=0.9)
    return pr

def savePageRank(pr, path, startPage, num_vertices, id2title):
    with open(path, 'w') as f:
        f.write(startPage + "\t" + str(num_vertices) + "\n")
        f.write("Pagerank\tTitle\n")
        for item in pr:
            f.write(str(round(item[1], 4)) + "\t" + id2title[item[0]].encode('utf8') + "\n")

def main(source_folder, start_page):
    id2title = {}
    level = 2
    with open(os.path.join(source_folder, str(level) + 'level-id2title.txt') , 'r') as f:
        for line in f.readlines():
            pageID, pageTitle = line.rstrip().split("\t")
            id2title[pageID] = pageTitle.decode('utf-8')
    path = os.path.join(source_folder, '2level-adjList.txt')
    g = nx.read_edgelist(path, create_using=nx.DiGraph(), nodetype=str)
    print(nx.info(g))

    plotGraph(g, id2title, source_folder)
    pr = run_pagerank(g)
    pr = sorted(pr.items(), key=itemgetter(1), reverse=True)
    savePageRank(pr, os.path.join(source_folder, 'ranking.txt'), start_page, len(pr), id2title)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="take graph information, plot graph, calculate PageRank, save into the same folder")
    parser.add_argument('-sf', '--source-folder')
    parser.add_argument('-sp', '--start-page')
    args = vars(parser.parse_args())
    main(args['source_folder'], args['start_page'])