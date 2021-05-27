from spleeter.separator import Separator
import pika
import json
import os

mqhost = os.environ.get("HOST")
mquser = os.environ.get("USER")
mqpass = os.environ.get("PASS")
mqport = os.environ.get("PORT")

credentials =  pika.PlainCredentials(mquser, mqpass)
connection = pika.BlockingConnection(pika.ConnectionParameters(mqhost, mqport,'/',credentials))
channel = connection.channel()

channel.queue_declare(queue='separate')
channel.queue_declare(queue='management')

def callback(ch, method, properties, body):
    vID = body.decode("utf-8")
    print(" [x] Received %s" % vID)
    # Using embedded configuration.
    separator = Separator('spleeter:2stems')
    # separator = Separator('spleeter:4stems')

    audio="/Audios/" + vID + ".wav"
    destination="/Separation"

    # Source Separation
    separator.separate_to_file(audio, destination)

    os.rename(audio, destination + "/" + vID + "/original.wav")
    os.remove("/Audios/" + vID + ".mp4")

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