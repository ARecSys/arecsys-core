
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import os
from elasticsearch import *

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

class Article( Base ):
    __tablename__ = 'articles_metadata'

    id = db.Column(db.String(50), primary_key = True) 
    doi = db.Column(db.String(100))
    title = db.Column(db.String())
    authors = db.Column(db.ARRAY(db.String))
    keywords = db.Column(db.ARRAY(db.String))
    fos =  db.Column(db.ARRAY(db.String))
    references = db.Column(db.ARRAY(db.String))

    def __repr__(self):
        return "<Article(doi='%s', id='%s', title='%s', authors='%s')>" % (
                                self.doi, self.id, self.title, self.authors )

    def getauthors( self ):
        return self.authors
        
    def toJSON(self):
        auth_str = ""
        if self.authors:
            auth_str = ';'.join( [ p for p in self.authors if p is not None ] )
        
        keywords_str = ""
        if self.keywords:
            keywords_str = ';'.join( [ k for k in self.keywords if k is not None ] )

        fos_str = ""
        if self.fos:
            fos_str = ';'.join( [ f for f in self.fos if f is not None ] )
        
        return { 
            "id": self.id,
            "doi" : self.doi, 
            "title" : self.title, 
            "authors" : auth_str, 
            "keywords" :  keywords_str, 
            "fos" : fos_str
        }

MAX_ARTICLES = 10000

def export_from_db_to_elastic_search():
    session = Session( engine )

    articles = session.query( Article ).limit( MAX_ARTICLES ).all()

    for art in articles:
        print( str ( art ) )
        resp = insert ( enginesearch, art.toJSON() )
        if resp[0]["errors"] != []:
            return -1
    
    return 0
