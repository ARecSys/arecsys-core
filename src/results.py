import json
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import os
import uuid

from src.algo import algofst, art_doi, art_id

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
    __tablename__ = 'results'
    id = db.Column(db.String(100), primary_key = True) 
    user_id = db.Column(db.String(100)) 
    article_id = db.Column(db.String(100))

    def serialize(self):
        return { 
            "user" : self.user_id, 
            "article_id" : self.article_id,
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
    
    session.query( Results ).filter( Results.user_id == user ).delete()
    session.commit()

    L_articles = art_id( recos )

    for article in L_articles:

        rst = Results( 
            id = str(uuid.uuid4()), 
            user_id = user, 
            article_id = article.doi
        ) 

        session.add( rst ) 

    session.commit()
