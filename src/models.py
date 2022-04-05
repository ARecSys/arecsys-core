from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import String

import os

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

engine = create_engine( database_uri )

session = Session(engine)

class Favorite( Base ):
    
    __tablename__ = 'fav_articles'
    
    id = Column(String(100), primary_key = True) 
    user = Column(String(50)) 
    doi = Column(String(100))
    title = Column(String(100))

    def serialize(self):
        return { 
            "user" : self.user, 
            "doi" : self.doi,
            "title" : self.title
        }

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

class Recommendation( Base ):
    
    __tablename__ = 'recommandations_fst'
    
    user_id = Column( String(100), primary_key = True ) 
    nodes = Column( ARRAY(String) )
    edges = Column(String)
    scores = Column(String)

    def serialize(self):
        return { 
            "user" : self.user_id, 
            "nodes" : self.nodes,
            "edges" : self.edges,
            "scores" : self.scores,
        }

# Base.metadata.create_all(engine)
