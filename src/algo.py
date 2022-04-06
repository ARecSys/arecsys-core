from models import Article
from models import session

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import json

def art_id(L_id:list = ["53e997e8b7602d9701fe00d3"]):
    '''
    Returns a list of the corresponding articles filtered by id.

            Parameters:
                    L_id (string[]): List of articles id.

            Returns:
                    out_articles (Articles[]): List of articles
    '''

    out_articles = session.query(Article).filter(Article.id.in_(tuple(L_id))).all()
    
    return out_articles

def art_doi(L_doi:list = ['10.1109/TBCAS.2011.2159859']):
    '''
    Returns a list of the corresponding articles filtered by doi.

            Parameters:
                    L_doi (string[]): List of articles doi.

            Returns:
                    out_articles (Articles[]): List of articles
    '''

    out_articles = session.query(Article).filter(Article.doi.in_(tuple(L_doi))).all()
    
    return out_articles
    
def voisins(articles:list):
    '''
    Returns a list of neighboring articles.

            Parameters:
                    articles (Articles[]): List of articles.

            Returns:
                    res (Articles[]): List of articles
    '''

    neighbourhood2 = [article.id for article in articles]
    for art in articles:
        if art.references is not None:
            
            neighboorhood2 =  np.unique(neighbourhood2 + art.references)
            
    res = session.query(Article).filter(Article.id.in_(tuple(neighboorhood2))).all()
    
    return res


def algofst(L_id:list = ["53e997e8b7602d9701fe00d3"], draw_graph:bool = False, dist_voisins:int = 2):
    '''
    Generate a graph of the friends of the friends of the friends (depth = dist_voisins). Compute the pagerank algorithm on this set

            Parameters:
                    L_id (string[]): List of articles id.
                    draw_graph (bool): Whether to draw the graph in matplotlib.
                    dist_voisins (int): Depth of references explored.

            Returns:
                    recommandation_ouput (json): a graph in json format.

                    recommandation_ouput = {
                        "nodes": list,
                        "edges": string,
                        "score": string,
                    }
    '''

    articles_dep = art_id(L_id)
    articles = articles_dep
    for i in range(dist_voisins):
        articles = voisins(articles)
    
    voisins_art = list(set(articles)) #unique articles
    G = nx.DiGraph()
    liste_sommet = [x.id for x in voisins_art]

    for art in voisins_art:
        G.add_node(art.id)
        if art.references is not None:
            for ref in art.references:
                if ref in liste_sommet:
                    G.add_node(ref)
                    G.add_edge(art.id, ref )

    if draw_graph:
        nx.draw(G, with_labels=True, arrowsize = 30, width = 2)#, labels=labels)
        
        plt.show()
    pr = nx.pagerank(G)
    ### Delete the ranking of the already read papers
    for article_input in L_id:
        pr.pop(article_input, None)
    res_id = sorted(pr, key=pr.get, reverse = True)[:10]
    res_score = [pr[_] for _ in res_id]
    res = art_id(res_id) 
    
    for y in pr.keys():
        
        pr[y] *= (10 / sum(res_score) )
    res += articles_dep
    res_G = nx.DiGraph()
    liste_res =   [x.id for x in res]
    for art in res:
        res_G.add_node(art.id)
        if art.references is not None:
            for ref in art.references:
                if ref in liste_res:
                    
                    res_G.add_node(ref)
                    res_G.add_edge(art.id, ref )
    liste_color = ['blue' if art in articles_dep else 'green' for art in res]
    liste_size = [300 if art in articles_dep else 300 * pr[art.id] for art in res ]
    if draw_graph:
        nx.draw_networkx(
            res_G,
            pos=nx.spring_layout(res_G),
            node_color = liste_color,
            node_size = liste_size)
        
        plt.show()
    L_nodes = res_G.nodes
    L_edges = res_G.edges

    nodes_with_title = [art.title for art in art_id(L_nodes)]
    
    edges_with_title = []
    for edge in list(L_edges):
        u, v = edge[0], edge[1]
        article_u, article_v = art_id([u])[0], art_id([v])[0]
        edge_with_title = [article_u.title, article_v.title]
        edges_with_title.append(edge_with_title)

    recommandation_ouput = {}
    recommandation_ouput["nodes"] = nodes_with_title
    recommandation_ouput["edges"] = json.dumps( edges_with_title )
    recommandation_ouput["scores"] = json.dumps( pr )
    
    return recommandation_ouput


def co_citation(L_id = ["53e997e8b7602d9701fe00d3"]):
    '''
    

    Parameters
    ----------
    L_id : list of string, optional
        list of articles_id. The default is ["53e997e8b7602d9701fe00d3"].

    Returns
    -------
    dic_cite : dictionnary
        key : articles (of type articles)
        values: number of citations in common (int)

    '''
    articles = art_id(L_id)
    voisins_art =  [x for x  in voisins(articles) if x not in articles]
    dic_cite = {}
    for x in voisins_art:
        our_articles = session.query(Article).filter(Article.references.contains({x.id})).all()
        for y in our_articles:
            if y not in dic_cite.keys():
                dic_cite[y] = 1
            else:
                dic_cite[y] += 1
    dic_cite = dict(sorted(dic_cite.items(), key=lambda item: item[1]))
    return dic_cite


def co_authors(L_id = ["53e997e8b7602d9701fe00d3"]):
    '''
    

    Parameters
    ----------
    L_id : list of string, optional
        list of articles_id. The default is ["53e997e8b7602d9701fe00d3"].

    Returns
    -------
    dic_aut : dictionnary
        key : articles of the class articles
        values: number of authors in common for L_id (int)

    '''
    articles = art_id(L_id)
    L_authors = []
    for x in articles:
        L_authors += x.authors
    L_authors = list(set(L_authors))
    dic_aut = {}
    for y in L_authors:
        
        our_articles = session.query(Article).filter(Article.authors.contains({y})).all()
        for z in our_articles:
            if z not in dic_aut.keys():
                dic_aut[z] = 1
            else:
                dic_aut[z] += 1
    dic_aut = dict(sorted(dic_aut.items(), key=lambda item: item[1]))
    for key in dic_aut.keys():
        if key in L_authors:
            dic_aut.pop(key, None)
    return dic_aut
def normalise(D):
    '''
    

    Parameters
    ----------
    D : dict with values of type float
        

    Returns
    -------

    Modify in place the dict by the sum of all values
    '''
    factor=1.0/sum(D.itervalues())
    for k in D:
        D[k] = D[k]*factor
        
def overall_score(L_id = ["53e997e8b7602d9701fe00d3"], i_cocite = 0.2, i_coaut= 0.6, i_graph = 0.2):
    '''
    

    Parameters
    ----------
    L_id : list of strings, optional
        list of articles ID. The default is ["53e997e8b7602d9701fe00d3"].
    i_cocite : weight of the cocited algorithm (float), optional
         The default is 0.4.
    i_coaut : weight of the coauthors algorithm (float), optional
         The default is 0.4.
    i_graph : weight of the pagerank algorithm (float), optional
         The default is 0.2.

    Returns
    -------
    Overall score of the recommendation by all 3 methods combined.
    dic_res : dictionnary of tuple (article (of type article), recommendation score(float))
    '''
    
            
            
    dic_aut = co_authors(L_id)
    dic_cite = co_citation(L_id)
    (dic_graph, L_nodes,L_edges,liste_size,liste_color) = algofst(L_id)
    
    
    
    keys = list(dic_aut.keys()) + list(dic_cite.keys()) + list(dic_graph.keys())
    keys = list(set(keys))
    dic_res = {}
    normalise(dic_cite)
    normalise(dic_aut)
    normalise(dic_graph)
    for x in keys:
        dic_res[x] = 0
        if x.id in dic_cite.keys():
            dic_res[x.id] += dic_cite[x]
        if x.id in dic_aut.keys():
            dic_res[x.id] += dic_aut[x]
        if x in dic_graph.keys():
            dic_res[x] += dic_graph[x]
            
    dic_res = dict(sorted(dic_res.items(), key=lambda item: item[1]))
    
    return dic_res
