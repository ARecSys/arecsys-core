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

class Results( Base ):
    __tablename__ = 'results_algofst'
    user_id = db.Column( db.String(100), primary_key = True ) 
    results = db.Column( db.ARRAY(db.String) )

    def serialize(self):
        return { 
            "user" : self.user_id, 
            "results" : self.results,
        }

def get_favorites( user ):
    session = Session(engine)
    
    return session.query( Favorite ).filter( Favorite.user == user ).all()

def compute_reco ( favorites ):
    
    dois = [ favorite.doi for favorite in favorites ]
    
    L_articles = art_doi( dois )
    
    ids = [ article.id for article in L_articles]

    return algofst( ids )

def publish_recos_in_db( user, recos ):
    
    session = Session(engine)
    
    result_by_user = session.query( Results ).filter( Results.user_id == user ).first()

    if result_by_user:
        result_by_user.results = recos
    
    else:
        rst = Results(
            user_id = user, 
            results = recos
        ) 

        session.add( rst ) 

    session.commit()
