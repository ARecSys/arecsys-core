# import azure.functions as func
import base64
import logging

from results import get_favorites, compute_reco, publish_recos_in_db
import pika, os, time

def algofst_process_function( msg ):
    
    user = msg.decode("utf-8")

    favorites = get_favorites( user )

    recos = compute_reco( favorites )
    
    publish_recos_in_db( user, recos )

# Access the CLODUAMQP_URL environment variable
url = os.environ["AMQP_URL"]
queue_name = "algofst_process"

params = pika.URLParameters( url )
connection = pika.BlockingConnection( params )
channel = connection.channel() # start a channel
channel.queue_declare( queue = queue_name ) # Declare a queue

# create a function which is called on incoming messages
def callback(ch, method, properties, body):
    algofst_process_function(body)

# set up subscription on the queue
channel.basic_consume( queue_name, callback, auto_ack = True)

# start consuming (blocks)
channel.start_consuming()
connection.close()
