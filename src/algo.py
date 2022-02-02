from tokenize import String
import json
from sqlalchemy import create_engine, Column, Integer, ARRAY, String, MetaData, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os

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

def algofst(L_id = ["53e997e8b7602d9701fe00d3"], draw_graph = False):
    '''
    Input : 
        L_id a list of id of the articles read
        
    Generate a graph of the friends of the friends of the friends
    Compute the pagerank algorithm on this set

    Returns
    -------
    Return None
    Print the top 5 articles

    '''
    articles = art_id(L_id)
    voisins_art =  voisins(voisins(articles))
    #print(len(voisins_art))
    voisins_art = list(set(voisins_art)) #unique articles
    #print(voisins_art)
    G = nx.DiGraph()
    liste_sommet = [x.id for x in voisins_art]

    for art in voisins_art:
        G.add_node(art.id)
        if art.references is not None:
            for ref in art.references:
                if ref in liste_sommet:
                    G.add_edge(art.id , ref )

    # print("liste_ref",liste_ref)
    # print("liste_sommet", liste_sommet)
    if draw_graph:
        nx.draw(G, with_labels=True)#, labels=labels)
        plt.show()
    pr = nx.pagerank(G)
    ### Delete the ranking of the already read papers
    for article_input in L_id:
        pr.pop(article_input, None)
    res_id = sorted(pr, key=pr.get, reverse = True)[:5]
    res_score = [pr[_] for _ in res_id]
    res = art_id(res_id)
    print(type(res))
    # print(res_id)
    # print(res_score)
    # print("Here is the top 5 articles recommended\n")
    # for x in res:
    #     print("Doi : {} with score {:.2f}".format(x.doi,pr[x.id]))
    return res
      
#%%
# session = Session(engine) 
# session.query(Article).filter(Article.id.in_(("123","456","53e997e8b7602d9701fe00d3"))).all()
# our_user = session.query(Article).filter_by(doi = '10.1109/TBCAS.2011.2159859').first()
# print(our_user._repr_())

