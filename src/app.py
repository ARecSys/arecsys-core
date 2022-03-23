from azure.storage.queue import ( QueueClient, BinaryBase64EncodePolicy, BinaryBase64DecodePolicy )
import base64
import os
from results import get_favorites, compute_reco, publish_recos_in_db
import time

# Retrieve the connection string from an environment
# variable named AZURE_STORAGE_CONNECTION_STRING
connect_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

# Create a unique name for the queue
q_name = "algofst"

# Instantiate a QueueClient object which will
# be used to create and manipulate the queue

queue_client = QueueClient.from_connection_string(
                            connect_str, 
                            q_name,
                            message_encode_policy = BinaryBase64EncodePolicy(),
                            message_decode_policy = BinaryBase64DecodePolicy()
                        )

while True:
    
    message = queue_client.receive_message()

    if message:
    
        user_public_id = base64.b64decode( message.content ).decode("utf-8")

        favorites = get_favorites( user_public_id )

        if favorites != []:

            recos = compute_reco( favorites )

            publish_recos_in_db( user_public_id, recos )
        
        queue_client.delete_message( message.id, message.pop_receipt )
    
    time.sleep( 60 )
