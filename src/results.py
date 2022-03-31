import json
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import os
import uuid

from algo import algofst, art_doi, art_id

Base = declarative_base()
# Update connection string information
hostname = os.environ["DB_HOSTNAME"]
dbname = os.environ["DB_NAME"]
user = os.environ["DB_USER"]
password = os.environ["DB_PASSWORD"]

database_uri = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}?sslmode=require'.format(
    dbuser=user,
    dbpass=password,
    dbhost=hostname,
    dbname=dbname
)

engine = db.create_engine( database_uri )

Base = declarative_base()

class Favorite( Base ):
    __tablename__ = 'fav_articles'
    id = db.Column(db.String(100), primary_key = True) 
    user = db.Column(db.String(50)) 
    doi = db.Column(db.String(100))
    title = db.Column(db.String(100))

    def serialize(self):
        return { 
            "user" : self.user, 
            "doi" : self.doi,
            "title" : self.title
        }

class Recommandation( Base ):
    __tablename__ = 'results_algofst'
    user_id = db.Column( db.String(100), primary_key = True ) 
    nodes = db.Column( db.ARRAY(db.String) )
    edges = db.Column(db.String)
    scores = db.Column(db.String)

    def serialize(self):
        return { 
            "user" : self.user_id, 
            "nodes" : self.nodes,
            "edges" : self.edges,
            "scores" : self.scores,
        }

def get_favorites( user ):
    session = Session(engine)
    
    return session.query( Favorite ).filter( Favorite.user == user ).all()

def compute_reco ( favorites ):
    
    dois = [ favorite.doi for favorite in favorites ]
    
    L_articles = art_doi( dois )
    
    ids = [ article.id for article in L_articles]

    return algofst( ids )

def publish_recos_in_db( user, recommandation_dict ):
    
    session = Session(engine)
    
    result_by_user = session.query( Recommandation ).filter( Recommandation.user_id == user ).first()

    if result_by_user:
        result_by_user.edges = recommandation_dict["edges"]
        result_by_user.nodes = recommandation_dict["nodes"]
        result_by_user.scores = recommandation_dict["scores"]
    
    else:
        rst = Recommandation(
            user_id = user, 
            edges = recommandation_dict["edges"],
            nodes = recommandation_dict["nodes"],
            scores = recommandation_dict["scores"]
        ) 

        session.add( rst ) 

    session.commit()
