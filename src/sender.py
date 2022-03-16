# example_publisher.py
import pika, os

# Parse CLODUAMQP_URL (fallback to localhost)
url = os.environ["AMQP_URL"]
queue_name = "algofst_process"

params = pika.URLParameters( url )
params.socket_timeout = 5

connection = pika.BlockingConnection(params) # Connect to CloudAMQP
channel = connection.channel() # start a channel
channel.queue_declare( queue = queue_name ) # Declare a queue
# send a message

channel.basic_publish( exchange = '', routing_key = queue_name, body = '0884f351-a002-4a64-88d2-a1c1ba86c59d' )
print ("[x] Message sent to consumer")
connection.close()
