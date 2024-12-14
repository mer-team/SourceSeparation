import pika
import os

def on_message(channel, method, properties, body):
    print(f"Received message: {body.decode()}")

def main():
    mq_host = os.environ.get("HOST", "127.0.0.1")
    mq_port = int(os.environ.get("PORT", 5672))
    mq_user = os.environ.get("USER", "merUser")
    mq_pass = os.environ.get("PASS", "passwordMER")
    queue_name = os.environ.get("QUEUE_NAME", "source_separation")

    credentials = pika.PlainCredentials(mq_user, mq_pass)
    parameters = pika.ConnectionParameters(host=mq_host, port=mq_port, credentials=credentials)
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    channel.queue_declare(queue=queue_name)
    
    channel.basic_consume(queue=queue_name, on_message_callback=on_message, auto_ack=True)
    
    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    main()
