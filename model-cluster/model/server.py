import math
from fastapi import FastAPI,HTTPException
from dotenv import load_dotenv
load_dotenv()

from persistence.kafka_consumer import start_consumer
from persistence.websockets import test_wb_connection, get_wb_connection

app = FastAPI()

@app.get("/")
def read_root():
    return {"messsage":"Bienvenido al servidor FastAPI"}

@app.get("/alarmas/{MotorId}")
def get_alertas(MotorId : str):
    pass