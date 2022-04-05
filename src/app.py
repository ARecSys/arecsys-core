from azure.storage.queue import ( QueueClient, BinaryBase64EncodePolicy, BinaryBase64DecodePolicy )
import base64
import os
from recommendation import get_favorites, compute_reco, update_recos_in_db
import time
from log import create_logger

logger = create_logger(__name__)

# Retrieve the connection string from an environment
# variable named AZURE_STORAGE_CONNECTION_STRING
connect_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

# Create a unique name for the queue
q_name = "algofst"

# Instantiate a QueueClient object which will
# be used to create and manipulate the queue
queue_client = QueueClient.from_connection_string(connect_str, q_name, message_encode_policy = BinaryBase64EncodePolicy(), message_decode_policy = BinaryBase64DecodePolicy())

logger.info('Started')

while True:
    
    message = queue_client.receive_message()

    if message:
        logger.info('----New message----')
        
        user_public_id = base64.b64decode(message.content).decode("utf-8")
        logger.info('user_public_id {user_public_id}'.format(user_public_id=user_public_id))
        
        favorites = get_favorites( user_public_id )

        if favorites != []:
            logger.info('Computing recommendations')
            recos = compute_reco( favorites )

            logger.info('Updating results in db')
            update_recos_in_db( user_public_id, recos )

        logger.info('Removing msg from queue')
        queue_client.delete_message( message.id, message.pop_receipt )
        
        logger.info('Waiting...')
    
    time.sleep( 30 )
