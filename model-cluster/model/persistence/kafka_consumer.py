from kafka import KafkaConsumer
import json
import os 
import threading

KAFKA_HOST = os.getenv('KAFKA_HOST')
vibration_data_list = []

def consume_vibration_data():
    global vibration_data_list
    try:
        # Crear consumidor de kafka
        vibration_consumer = KafkaConsumer(
            'vibration-topic',
            bootstrap_servers=KAFKA_HOST,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='vibraciones-group',
            value_deserializer=lambda x: x.decode('utf-8')
    )
        print("Conectado al broker de Kafka")   

        for mesage in vibration_consumer:
            vibration_data = mesage.value
            print(f"Datos recibidos: {vibration_data}")
        
            ## Verificacion de los campos esperados
            if all(key in vibration_data for key in ['idMotor','value','axis','medicion']):
                # Guardamos los datos en la lista
                data_array = [
                    vibration_data['idMotor'],
                    vibration_data['value'],
                    vibration_data['axis'],
                    vibration_data['medicion']
                ]

                vibration_data_list.append(data_array)
                print(f"Datos procesados y almacenados: {data_array}")

    except Exception as e:
        print(f"Error al conectarse o consumir datos de Kafka: {e}")

def start_consumer():
    thread = threading.Thread(target=consume_vibration_data)
    thread.daemon = True  # Permite que el hilo se cierre al cerrar la aplicación
    thread.start()