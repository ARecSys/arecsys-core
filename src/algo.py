from tokenize import String
import json
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os

from sqlalchemy.dialects.postgresql import ARRAY
# Update connection string information
hostname = os.environ["DB_HOSTNAME"]
dbname = os.environ["DB_NAME"]
user = os.environ["DB_USER"]
password = os.environ["DB_PASSWORD"]

Base = declarative_base()

database_uri = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}?sslmode=require'.format(
    dbuser=user,
    dbpass=password,
    dbhost=hostname,
    dbname=dbname
)

engine = create_engine(database_uri)

session = Session(engine)

class Article(Base):
    __tablename__ = 'articles_metadata'

    id = Column(String(50), primary_key = True) 
    doi = Column(String(100))
    title = Column(String())
    authors = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    fos =  Column(ARRAY(String))
    references = Column(ARRAY(String))

    def toJson(self):
        return {
            "doi" : self.doi, 
            "id" : self.id,
            "title" : self.title,
            "authors" : self.authors,
            "references": self.references
        }
        
    def __repr__(self):
        return "<Article(doi='%s', id='%s', title='%s', authors='%s', references='%s')>" % (
                                self.doi, self.id, self.title, self.authors, self.references )

def ask_doi():
    '''
    Ask the user the doi of the papers SEPARATED BY SPACE    
    Returns
    -------
    List of the articles of these doi


    '''
    L = []
    doi = str(input("Input the DOIs SEPARATED BY SPACE\n"))
    doi = doi.split(" ")
    
    for x in doi:
        our_user = session.query(Article).filter_by(doi = str(x)).all()
        L.append(our_user)
    
    return L
def art_id(L_id = ["53e997e8b7602d9701fe00d3"]):
    '''
    L_id is a list of the ID (primary key) of the papers
    Returns
    -------
    List of the corresponding articles (objects)


    '''
    our_articles = session.query(Article).filter(Article.id.in_(tuple(L_id))).all()
    return our_articles
def art_doi(L_doi = ['10.1109/TBCAS.2011.2159859']):
     '''
     L_doi is a list of the DOI (primary key) of the papers
     Returns
     -------
     List of the corresponding articles (objects)


     '''
     our_articles = session.query(Article).filter(Article.doi.in_(tuple(L_doi))).all()
     return our_articles
        
    
def voisins(L):
    '''
    
    L list of articles (object)
    Returns
    -------
    Table of the references of these articles (objects)
    
    '''
    neighbourhood2 = [x.id for x in L]
    for art in L:
        if art.references is not None:
            
            neighboorhood2 =  np.unique(neighbourhood2 + art.references)
            
    res = session.query(Article).filter(Article.id.in_(tuple(neighboorhood2))).all()
    
    return res


def algofst(L_id = ["53e997e8b7602d9701fe00d3"], draw_graph = False, dist_voisins = 2):
    '''
    Input : 
        L_id a list of id of the articles read
        
    Generate a graph of the friends of the friends of the friends
    Compute the pagerank algorithm on this set

    Returns
    -------
    Return None
    Print the top 10 articles with their scores and the associated graph

    '''
    articles_dep = art_id(L_id)
    articles = articles_dep
    for i in range(dist_voisins):
        articles = voisins(articles)
    
    #print(len(voisins_art))
    voisins_art = list(set(articles)) #unique articles
    #print(voisins_art)
    G = nx.DiGraph()
    liste_sommet = [x.id for x in voisins_art]

    for art in voisins_art:
        G.add_node(art.id)
        if art.references is not None:
            for ref in art.references:
                if ref in liste_sommet:
                    #print(art.id, ref)
                    G.add_node(ref)
                    G.add_edge(art.id, ref )

    # print("liste_ref",liste_ref)
    # print("liste_sommet", liste_sommet)
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
    
    # print(res_id)
    # print(res_score)
    #print("Here is the top 5 articles recommended\n")
    #for x in res:
    #    print("Doi : {} with score {:.2f}".format(x.doi,pr[x.id]))
    
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
                    #print(art.id, ref)
                    
                    res_G.add_node(ref)
                    res_G.add_edge(art.id, ref )
    liste_color = ['blue' if art in articles_dep else 'green' for art in res]
    liste_size = [300 if art in articles_dep else 300 * pr[art.id] for art in res ]
    nx.draw_networkx(
        res_G,
        pos=nx.spring_layout(res_G),
        node_color = liste_color,
        node_size = liste_size)
    
    plt.show()
    return res_G,res


def co_citation(L_id = ["53e997e8b7602d9701fe00d3"]):
    '''
    

    Parameters
    ----------
    L_id : list, optional
        list of articles_id. The default is ["53e997e8b7602d9701fe00d3"].

    Returns
    -------
    dic_cite : dictionnary
        key : articles
        values: number of citations in common

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
    L_id : list, optional
        list of articles_id. The default is ["53e997e8b7602d9701fe00d3"].

    Returns
    -------
    dic_aut : dictionnary
        key : articles
        values: number of authors in common for L_id

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
    D : dict
        DESCRIPTION.

    Returns
    -------
    None.
    Modify in place the dict by the sum of all values
    '''
    factor=1.0/sum(D.itervalues())
    for k in D:
        D[k] = D[k]*factor
        
def overall_score(L_id = ["53e997e8b7602d9701fe00d3"], i_cocite = 0.2, i_coaut= 0.6, i_graph = 0.2):
    '''
    

    Parameters
    ----------
    L_id : TYPE, optional
        DESCRIPTION. The default is ["53e997e8b7602d9701fe00d3"].
    i_cocite : TYPE, optional
        DESCRIPTION. The default is 0.4.
    i_coaut : TYPE, optional
        DESCRIPTION. The default is 0.4.
    i_graph : TYPE, optional
        DESCRIPTION. The default is 0.2.

    Returns
    -------
    Overall score of the 

    '''
    
            
            
    dic_aut = co_authors(L_id)
    dic_cite = co_citation(L_id)
    dic_graph = algofst(L_id)
    
    
    
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
            
    
    
