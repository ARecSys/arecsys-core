# example_consumer.py
import pika, os, time

def pdf_process_function(msg):
  print(" PDF processing")
  print(" [x] Received " + str(msg))

  time.sleep(5) # delays for 5 seconds
  print(" PDF processing finished")
  return

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
url = "amqps://ztgjagvs:79izXLrZTk1tB89fGKj-DeCkKSL1xjTk@rat.rmq2.cloudamqp.com/ztgjagvs"
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel() # start a channel
channel.queue_declare(queue='pdfprocess') # Declare a queue

# create a function which is called on incoming messages
def callback(ch, method, properties, body):
  pdf_process_function(body)

# set up subscription on the queue
channel.basic_consume('pdfprocess',
  callback,
  auto_ack=True)

# start consuming (blocks)
channel.start_consuming()
connection.close()
