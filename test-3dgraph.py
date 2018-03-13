from __future__ import print_function, unicode_literals
import networkx as nx
import matplotlib.pyplot as plt
import sys, os
reload(sys)
sys.setdefaultencoding("ISO-8859-1")
from operator import itemgetter
import argparse
import plotly
import plotly.plotly as py
from plotly.graph_objs import *
plotly.tools.set_credentials_file(username='tset0401', api_key='aAXy7euxzenbSECeVX5I')

def plotGraph(g, id2title):
    layt = nx.spring_layout(g, dim=3)
    Edges = g.edges()
    plt.axis('off')
    
    Xn=[layt[k][0] for k in id2title]# x-coordinates of nodes
    Yn=[layt[k][1] for k in id2title]# y-coordinates
    Zn=[layt[k][2] for k in id2title]# z-coordinates
    Xe=[]
    Ye=[]
    Ze=[]
    for e in Edges:
        Xe+=[layt[e[0]][0],layt[e[1]][0], None]# x-coordinates of edge ends
        Ye+=[layt[e[0]][1],layt[e[1]][1], None]
        Ze+=[layt[e[0]][2],layt[e[1]][2], None]
    
    trace1=Scatter3d(x=Xe,
               y=Ye,
               z=Ze,
               mode='lines',
               line=Line(color='rgb(125,125,125)', width=1),
               hoverinfo='none'
               )
    trace2=Scatter3d(x=Xn,
                y=Yn,
                z=Zn,
                mode='markers',
                name='actors',
                marker=Marker(symbol='dot',
                                size=6,
                                color=id2title.keys(),
                                colorscale='Viridis',
                                line=Line(color='rgb(50,50,50)', width=0.5)
                                ),
                text=id2title.values(),
                hoverinfo='text'
                )
        
    axis=dict(showbackground=False,
          showline=False,
          zeroline=False,
          showgrid=False,
          showticklabels=False,
          title=''
          )

    layout = Layout(
         title="Network of wiki pages (3D visualization)",
         width=1000,
         height=1000,
         showlegend=False,
         scene=Scene(
         xaxis=XAxis(axis),
         yaxis=YAxis(axis),
         zaxis=ZAxis(axis),
        ),
     margin=Margin(
        t=100
    ),
    hovermode='closest',
    annotations=Annotations([
           Annotation(
           showarrow=False,
            text="Data source: http://vi.wikipedia.org",
            xref='paper',
            yref='paper',
            x=0,
            y=0.1,
            xanchor='left',
            yanchor='bottom',
            font=Font(
            size=14
            )
            )
        ]),)
    data=Data([trace1, trace2])
    fig=Figure(data=data, layout=layout)
    py.iplot(fig)

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

    plotGraph(g, id2title)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="take graph information, plot graph, calculate PageRank, save into the same folder")
    parser.add_argument('-sf', '--source-folder')
    parser.add_argument('-sp', '--start-page')
    args = vars(parser.parse_args())
    main(args['source_folder'], args['start_page'])