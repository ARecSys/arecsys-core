from models import Favorite
from models import Recommendation
from models import session

from algo import algofst, art_doi

def get_favorites( user ):
    
    return session.query( Favorite ).filter( Favorite.user == user ).all()

def compute_reco ( favorites ):
    
    dois = [ favorite.doi for favorite in favorites ]
    
    L_articles = art_doi( dois )
    
    ids = [ article.id for article in L_articles]

    return algofst( ids )

def update_recos_in_db( user, Recommendation_dict ):
       
    result_by_user = session.query( Recommendation ).filter( Recommendation.user_id == user ).first()

    if result_by_user:
        result_by_user.edges = Recommendation_dict["edges"] 
        result_by_user.nodes = Recommendation_dict["nodes"]
        result_by_user.scores = Recommendation_dict["scores"] 
    
    else:
        rst = Recommendation(
            user_id = user, 
            edges = Recommendation_dict["edges"],
            nodes = Recommendation_dict["nodes"],
            scores = Recommendation_dict["scores"]
        ) 

        session.add( rst ) 

    session.commit()
