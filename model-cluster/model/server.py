import math
from fastapi import FastAPI,HTTPException
from dotenv import load_dotenv
load_dotenv()
import os
from persistence.kafka_consumer import start_consumer,vibration_data_list
##from persistence.websockets import test_wb_connection, get_wb_connection

app = FastAPI()

@app.get("/")
def read_root():
    return {"messsage":"Bienvenido al servidor FastAPI"}

@app.get("/velocity/{idMotor}")
def get_velocity_data(idMotor:str):
    velocity_data = [d for d in vibration_data_list if d['idMotor'] == idMotor and d['medicion'] == 'velocity']

    if not velocity_data:
        raise HTTPException(status_code=404, detail=f"No se encontró información de velocidad para el motor {idMotor}")
    
    picos = [d for d in velocity_data if d['Value'] > 12 ]

    # Aqui colocaremos la logica para el calculo de los picos
    return {
        "idMotor": idMotor,
        "picos": picos,
        "message": f"Se encontraron {len(picos)} picos en la velocidad" 
    }


@app.get("/aceleration/{idMotor}")
def get_aceleration_data(idMotor:str):
    aceleration_data = [d for d in vibration_data_list if d['idMotor'] == idMotor and d['medicion'] == 'aceleration']

    if not aceleration_data:
        raise HTTPException(status_code=404, detail=f"No se encontró información de velocidad para el motor {idMotor}")

    # Logica para calcular Rms
    rms = math.sqrt(sum([d['value']**2 for d in aceleration_data]) / len(aceleration_data))

    return {
        "idMotor": idMotor,
        "rms": rms,
        "message": f"Se encontro que el valor de rms para el motor {idMotor} es de {rms}"
    }

@app.get("/temperature/{idMotor}")
def get_temperature_data(idMotor:str):
    temperature_data = [d for d in vibration_data_list if d['idMotor'] == idMotor and d['medicion'] == 'temperature']

    if not temperature_data:
        raise HTTPException(status_code=404, detail=f"No se encontró información de velocidad para el motor {idMotor}")        

    ## Logica para el calculo de temperatura global
    promedio = sum([d['Value'] for d in temperature_data] / len(temperature_data))

    return {
        "idMotor":idMotor,
        "promedio": promedio,
        "message":f"Se encontro que la temperatura promedio es {promedio}"
    }

if __name__ == "__main__":
    import uvicorn
    start_consumer()
    uvicorn.run(app,host = "0.0.0.0",port=8000)