from spleeter.separator import Separator

from time import perf_counter #from https://www.geeksforgeeks.org/time-perf_counter-function-in-python/

import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='separate')
channel.queue_declare(queue='segmentation')

def callback(ch, method, properties, body):
    vID = body.decode("utf-8")
    print(" [x] Received %s" % vID)
    # Using embedded configuration.
    separator = Separator('spleeter:2stems')
    # separator = Separator('spleeter:4stems')

    audio="/vagrant/VidExtractor/" + vID + ".wav"
    destination="./Output"

    # Start the stopwatch / counter 
    t1_start = perf_counter()  

    separator.separate_to_file(audio, destination)

    # Stop the stopwatch / counter 
    t1_stop = perf_counter() 
    print("Elapsed time in seconds:", t1_stop-t1_start) 

    msg = {
        "Service": "SourceSeparation",
        "Result": { "vID": vID }
    }

    channel.basic_publish(exchange='',
                        routing_key='management',
                        body=json.dumps(msg))
    print(" [x] Sent %s to management" % msg)

channel.basic_consume(queue='separate',
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()