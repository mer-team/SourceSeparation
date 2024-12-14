import json
import os
import time
import pika
from spleeter.separator import Separator

mq_host = os.environ.get("HOST", "localhost")
mq_port = int(os.environ.get("PORT", 5672))
mq_user = os.environ.get("USER", "guest")
mq_pass = os.environ.get("PASS", "guest")
queue_in = os.environ.get("QUEUE_IN", "source-separation")
queue_out = os.environ.get("QUEUE_OUT", "mer-management")
audio_files_folder = "/Audios"
greenCheckbox = "\x1b[32m\u2713\x1b[0m"; # Green checkbox with ANSI escape codes
yellowInfo = "\x1b[33mℹ\x1b[0m"; # Yellow info character with ANSI escape codes
redCrossmark = "\x1b[31m\u274C\x1b[0m"; # Red crossmark with ANSI escape codes

connection = None

def send_response_to_queue(channel, response, queue_name):
    debug_message = f"Will now push to RabbitMQ {queue_name} the response: {response}"
    print(debug_message, flush=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(response)
    )
    print("Response sent:", response)

def process(input_file_name, stems):
    file_path = os.path.join(audio_files_folder, input_file_name)

    if os.path.exists(file_path) == False:
        print("File does not exist.")
        return None
    
    base_name = os.path.basename(file_path)  # Get the base filename
    file_name_without_extension, extension = os.path.splitext(base_name)  # Separate base filename and extension

    # Generate the base JSON response
    output = {
        "vocals": f"{file_name_without_extension}-vocals{extension}",
    }
    
    try:
        separator = None

        if (stems == 2):
            separator = Separator('spleeter:2stems')
            output['accompaniment'] = f"{file_name_without_extension}-accompaniment{extension}"
        elif (stems == 4):
            separator = Separator('spleeter:4stems')
            output['drums'] = f"{file_name_without_extension}-drums{extension}"
            output['bass'] = f"{file_name_without_extension}-bass{extension}"
            output['other'] = f"{file_name_without_extension}-other{extension}"
        elif (stems == 5):
            separator = Separator('spleeter:5stems')
            output['drums'] = f"{file_name_without_extension}-drums{extension}"
            output['bass'] = f"{file_name_without_extension}-bass{extension}"
            output['piano'] = f"{file_name_without_extension}-piano{extension}"
            output['other'] = f"{file_name_without_extension}-other{extension}"
        else:
            # TODO ERROR LOGGING
            return None
        
        # Spleeter source separation call
        debug_message = f"input: {file_path}, output: {audio_files_folder}"
        print(debug_message)
        separator.separate_to_file(file_path, audio_files_folder, filename_format="{filename}-{instrument}.{codec}")
        print (output)
        return output

    except Exception as error:
        print("Error while processing: " + error)
        return None


def on_message(channel, method, properties, body):
    try:
        data = json.loads(body)
        input_file_name = data.get("inputFile")
        stems = int(data.get("stems"))

        response = {
            "inputFile": input_file_name,
            "songId": data.get("songId"),
            "status": False,
            "timestamp": int(time.time())
        }
        
        if input_file_name is None or stems not in [2, 4, 5]:
            print("Invalid JSON message")
            # TODO SEND ERROR
            return
        
        separated_files = process(input_file_name, stems)
        
        if (separated_files == None):
            send_response_to_queue(channel, response, queue_out)
        else:
            print(response)
            response.update(separated_files)
            print(response)
            send_response_to_queue(channel, response, queue_out)
        
    except json.JSONDecodeError:
        print("Invalid JSON format")
        # TODO SEND ERROR


def main():
    # global connection # Make sure to use the global connection variable
    try:
        # connection = pika.BlockingConnection(pika.ConnectionParameters(
        #     host=mq_host, port=mq_port, credentials=pika.PlainCredentials(mq_user, mq_pass)))
        
        # debug_message = f"MQ User: {mq_user}, MQ Pass: {mq_pass}, MQ Host: {mq_host}, MQ Port: {mq_port}"
        # print(debug_message)

        credentials = pika.PlainCredentials(mq_user, mq_pass)
        connection = pika.BlockingConnection(pika.ConnectionParameters(mq_host, mq_port, '/', credentials))
        # print(connection)

        channel = connection.channel()
        channel.queue_declare(queue=queue_in)
        channel.queue_declare(queue=queue_out)

        channel.basic_consume(queue=queue_in, on_message_callback=on_message, auto_ack=True)
        
        print(f" [{yellowInfo}] Waiting for messages on RabbitMQ queue \"{queue_in}\". To exit press CTRL+C", flush=True)
        channel.start_consuming()
    except Exception as exc:
        print("Error connecting to RabbitMQ: ")
        print(exc)

if __name__ == '__main__':
    main()












# mqhost = os.environ.get("HOST", "localhost")
# mquser = os.environ.get("USER", "guest")
# mqpass = os.environ.get("PASS", "guest")
# mqport = os.environ.get("PORT", 5672)
# queue_in = os.environ.get("QUEUE_IN", "source-separation")
# queue_out = os.environ.get("QUEUE_OUT", "mer-manager")

# credentials =  pika.PlainCredentials(mquser, mqpass)
# connection = pika.BlockingConnection(pika.ConnectionParameters(mqhost, mqport,'/',credentials))
# channel = connection.channel()

# channel.queue_declare(queue=queue_in)
# channel.queue_declare(queue=queue_out)

# def callback(ch, method, properties, body):
#     vID = body.decode("utf-8")
#     print(" [x] Received %s" % vID)
#     # Using embedded configuration.
#     separator = Separator('spleeter:2stems')
#     # separator = Separator('spleeter:4stems')

#     audio="/Audios/" + vID + ".wav"
#     destination="/Audios"

#     # PLAN
#     # receive message from queue
#     # JSON message with:
#     # - inputFile
#     # - outputSettings
#     #  - stems to use 2, 4 or 5
#     #  - anything more? output filename or outputdir?
#     # perform separation (wait for it?)
#     # output JSON response with:
#     #   - the inputFile that was separated (or task ID later?)
#     #   - stems used
#     #   - resulting files (with key: filename or later filepath?)
#     # sent to queue

#     # Source Separation
#     separator.separate_to_file(audio, destination, filename_format="{filename}-{instrument}.{codec}")
#     separator.separate_to_file(audio, destination)

#     os.rename(audio, destination + "/" + vID + "/original.wav")
#     # os.remove("/Audios/" + vID + ".mp4")

#     msg = {
#         "Service": "SourceSeparation",
#         "Result": { "vID": vID }
#     }

#     channel.basic_publish(exchange='',
#                         routing_key='management',
#                         body=json.dumps(msg))
#     print(" [x] Sent %s to management" % msg)

# channel.basic_consume(queue='separate',
#                       auto_ack=True,
#                       on_message_callback=callback)

# print(' [*] Waiting for messages. To exit press CTRL+C')
# channel.start_consuming()