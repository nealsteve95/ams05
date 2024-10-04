from kafka import KafkaConsumer
from .sql_postgres import get_pg_server_connection
import json
import os 
import threading

KAFKA_HOST = os.getenv('KAFKA_HOST')

## Definir los datos que va a enviar 
def store_rating(user_id, movie_id, rating):
    conn = get_pg_server_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO UserRatings (user_id, movie_id, rating) VALUES (%s, %s, %s) "
            "ON CONFLICT (user_id, movie_id) DO UPDATE SET rating = EXCLUDED.rating",
            (user_id, movie_id, rating)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error storing rating: {e}")
    finally:
        cursor.close()
        conn.close()

def consume_votes():
    consumer = KafkaConsumer(
        'votes-topic',
        bootstrap_servers=KAFKA_HOST,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='votes-group',
        value_deserializer=lambda x: x.decode('utf-8')
    )

    for message in consumer:
        vote = json.loads(message.value)
        store_rating(vote["user_id"], vote["movie_id"], vote["rating"])

def start_consumer():
    thread = threading.Thread(target=consume_votes)
    thread.daemon = True  # Permite que el hilo se cierre al cerrar la aplicación
    thread.start()