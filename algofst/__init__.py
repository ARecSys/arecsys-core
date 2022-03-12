import azure.functions as func
import base64
import logging

from src.results import get_favorites, compute_reco, publish_recos_in_db

def main( msg: func.QueueMessage ) -> None:

    user = base64.b64decode( msg.get_body() ).decode("utf-8")

    favorites = get_favorites( user )

    recos = compute_reco( favorites )
    
    publish_recos_in_db( user, recos )
