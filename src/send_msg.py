from azure.storage.queue import (
        QueueClient,
        BinaryBase64EncodePolicy,
        BinaryBase64DecodePolicy
)
import base64
# Retrieve the connection string from an environment
# variable named AZURE_STORAGE_CONNECTION_STRING
connect_str = "DefaultEndpointsProtocol=https;AccountName=arecsysstorage;AccountKey=rveE3HC1t1noAum0lR5j5Tf1Tr0THikLRO7SP2BOwS/CHzBWxrhgVzxwpyYpA3e6JCCyoPyIrhMe+AStAl9SqA==;EndpointSuffix=core.windows.net"

# Create a unique name for the queue
q_name = "reco"

# Instantiate a QueueClient object which will
# be used to create and manipulate the queue
print("Creating queue: " + q_name)

queue_client = QueueClient.from_connection_string(connect_str, q_name ,message_encode_policy = BinaryBase64EncodePolicy(),
                            message_decode_policy = BinaryBase64DecodePolicy()
                        )

message = "Python is fun"
print("Adding message: " + message)
message_bytes = message.encode('ascii')
base64_bytes = base64.b64encode(message_bytes)

queue_client.send_message( base64_bytes )
