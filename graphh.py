#!/bin/python
#coding: utf-8
# building and visualizing social graph
from igraph import *
import math

def richclub(graph, fraction=0.1, highest=True, scores=None, indices_only=False):
    """Extracts the "rich club" of the given graph, i.e. the subgraph spanned
    between vertices having the top X% of some score.
 
    Scores are given by the vertex degrees by default.
 
    @param graph:    the graph to work on
    @param fraction: the fraction of vertices to extract; must be between 0 and 1.
    @param highest:  whether to extract the subgraph spanned by the highest or
                     lowest scores.
    @param scores:   the scores themselves. C{None} uses the vertex degrees.
    @param indices_only: whether to return the vertex indices only (and not the
                         subgraph)
    """
 
    if scores is None:
        scores = graph.degree()
 
    indices = range(graph.vcount())
    indices.sort(key=scores.__getitem__)
 
    n = int(round(graph.vcount() * fraction))
    if highest:
        indices = indices[-n:]
    else:
        indices = indices[:n]
 
    if indices_only:
        return indices
 
    return graph.subgraph(indices)

def ljgraph(data,target,platform):
    bloggers = {}
    for person in data:
	res = person
	if len(res) == 5:
	    (name,posts,comments,friends,pic) = res
	else:
	    res.append("zero")
	    (name,posts,comments,friends,pic) = res
	reads = friends.strip().split(',')
	name = name.strip()
	bloggers[name] = {}
	bloggers[name]["posts"] = posts
	bloggers[name]["comments"] = comments
	bloggers[name]["reads"] = reads
	bloggers[name]["pic"] = pic
    # print bloggers.keys()

    g = Graph(len(bloggers))
    g = g.as_directed()
    g.vs["name"] = [word.encode('utf-8') for word in bloggers.keys()]
    g.vs["label"] = g.vs["name"]

    #g.Read_GraphML('target.graphml')
    for vertex in g.vs:
	name2 = vertex["name"].decode('utf-8')
	vertex["reads"] = len(bloggers[name2]['reads'])
	vertex["posts"] = bloggers[name2]["posts"]
	vertex["comments"] = bloggers[name2]["comments"]
	vertex["pic"] = bloggers[name2]["pic"]
	if vertex["name"] == target:
	    vertex["color"] = "black"
	    vertex["shape"] = "diamond"
    
    for i in bloggers:
	blogger = (g.vs.find(name=i.encode('utf-8'))).index
	for el in bloggers[i]['reads']:
	    if el in bloggers.keys():
		friend = (g.vs.find(name=el.encode('utf-8'))).index
		g.add_edge(blogger,friend)

    layout = g.layout("kk")
    visual_style = {}
    if platform == "lj":
	visual_style["vertex_label_size"] = [math.log10(float(post)+1)*12.0 for post in g.vs["posts"]]
	visual_style["vertex_size"] = [math.log10(float(post)+1)*12.0 for post in g.vs["posts"]]
    else:
	visual_style["vertex_label_size"] = 40
	visual_style["vertex_size"] = 40
    visual_style["bbox"] = (2048, 2048)
    visual_style["layout"] = layout
    visual_style["margin"] = 100
    visual_style["arrow_size"] = 2
    
    visual_style_top = {}
    visual_style_top["vertex_color"] = "orange"
    if platform == "lj":
	visual_style_top["vertex_label_size"] = [math.log10(float(post)+1)*8 for post in g.vs["posts"]]
	visual_style_top["vertex_size"] = [math.log10(float(post)+1)*8 for post in g.vs["posts"]]
    else:
	visual_style_top["vertex_label_size"] = 80
	visual_style_top["vertex_size"] = 80
    visual_style_top["bbox"] = (2048, 2048)
    visual_style_top["layout"] = layout
    visual_style_top["margin"] = 50
    
    def processgraph(g,typeg):
	#print summary(g)
	g.write_graphml(target+'.graphml')

	maxbet = max(g.betweenness())
	max_eb = max(g.edge_betweenness())
	vertexnumber = len(g.vs)
	edgesnumber = len(g.es)
	maxbetweenness = (maxbet, g.vs[g.betweenness().index(maxbet)]["name"])
	[(one,two)] = [g.es[idx].tuple for idx, eb in enumerate(g.edge_betweenness()) if eb == max_eb]
	maxedgebetweenness = (one,two,g.vs[one]["name"],g.vs[two]["name"])
	#print "Components:",'\n',g.components(),'\n'
	maxcore = max(g.shell_index())
	core = g.k_core(maxcore)

	plot(g, '/var/www/websocgraph/static/img/'+target+"_"+typeg+'.svg', **visual_style)
	plot(core,'/var/www/websocgraph/static/img/'+target+"_"+typeg+'_maxcore.svg',**visual_style_top)

    
	rich_degrees = richclub(g,fraction=0.1, highest=True, scores=g.degree(type="in"))
	visual_style_top["vertex_size"] = [float(post)*10 for post in g.degree(type="in")]
	visual_style_top["vertex_label_size"] = [float(post)*10 for post in g.degree(type="in")]
	plot(rich_degrees,'/var/www/websocgraph/static/img/'+target+"_"+typeg+'_rich_degrees_in.svg', **visual_style_top)
	
	if typeg == "withouttarget":
	    rich_betweennes = richclub(g,fraction=0.1, highest=True,scores=g.betweenness())
	    #visual_style_top["vertex_size"] = [float(post)*100 for post in rich_betweennes.betweenness()]
	    #visual_style_top["vertex_label_size"] = [float(post)*100 for post in rich_betweennes.betweenness()]
	    plot(rich_betweennes,'/var/www/websocgraph/static/img/'+target+"_"+typeg+'_rich_between.svg',**visual_style_top)

	rich_pagerank = richclub(g,fraction=0.1, highest=True,scores=g.pagerank())
	visual_style_top["vertex_size"] = [float(post)*700 for post in rich_pagerank.pagerank()]
	visual_style_top["vertex_label_size"] = [float(post)*200 for post in rich_pagerank.pagerank()]
	plot(rich_pagerank,'/var/www/websocgraph/static/img/'+target+"_"+typeg+'_rich_prank.svg',**visual_style_top)
    
	communities_walktrap = g.community_walktrap()
	#print "Communities Walktrap:", communities_walktrap

	if typeg == "target":
	    communities_spinglass = g.community_spinglass()
	    #print "Communities spinglass:", communities_spinglass
	    modularity_spinglass = g.modularity(communities_spinglass)
	    plot(communities_spinglass,'/var/www/websocgraph/static/img/'+target+"_"+typeg+'_spinglass.svg', **visual_style)
	    #print "Modularity Spinglass:",modularity_spinglass
	else:
	    communities_infomap = g.community_infomap(vertex_weights="posts", trials=10)
    	    #print "Communities Infomap:", communities_infomap
    	    modularity_infomap = g.modularity(communities_infomap)
	    plot(communities_infomap,'/var/www/websocgraph/static/img/'+target+"_"+typeg+'_infomap.svg', **visual_style)
	    #print "Modularity Infomap:",modularity_infomap
    
	plot(communities_walktrap,'/var/www/websocgraph/static/img/'+target+"_"+typeg+'_walktrap.svg',orientation="vertical", **visual_style)

	return vertexnumber,edgesnumber,maxbetweenness,maxedgebetweenness,maxcore
    a = processgraph(g,"target")
    visual_style_top = {}
    visual_style_top["vertex_color"] = "orange"
    if platform == "lj":
	visual_style_top["vertex_label_size"] = [math.log10(float(post)+1)*8 for post in g.vs["posts"]]
	visual_style_top["vertex_size"] = [math.log10(float(post)+1)*8 for post in g.vs["posts"]]
    else:
	visual_style_top["vertex_label_size"] = 80
	visual_style_top["vertex_size"] = 80
    visual_style_top["bbox"] = (2048, 2048)
    visual_style_top["layout"] = layout
    visual_style_top["margin"] = 50
    g.delete_vertices(g.vs.find(name=target).index)
    b = processgraph(g,"withouttarget")
    return a,b