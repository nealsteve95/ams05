import math
from fastapi import FastAPI,HTTPException,File,UploadFile
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from persistence.websockets import websocket_endpoint,send_updates
from fastapi import WebSocket
load_dotenv()
import os
from persistence.kafka_consumer import start_consumer,vibration_data_list
import pandas as pd 

app = FastAPI()

@app.get("/")
def read_root():
    return {"messsage":"Bienvenido al servidor FastAPI"}

@app.websocket("/ws")
async def websocket_route(websocket : WebSocket):
    await websocket_endpoint(websocket) 

@app.get("/velocity/{idMotor}")
async def get_velocity_data(idMotor:str):
    velocity_data = [d for d in vibration_data_list if d['idMotor'] == idMotor and d['medicion'] == 'velocity']

    if not velocity_data:
        raise HTTPException(status_code=404, detail=f"No se encontró información de velocidad para el motor {idMotor}")
    
    picos = [d for d in velocity_data if d['Value'] > 12 ]

    # Aqui colocaremos la logica para el calculo de los picos
    result = {
        "idMotor": idMotor,
        "picos": picos,
        "message": f"Se encontraron {len(picos)} picos en la velocidad" 
    }

    #Envio de resultados al websockets
    await send_updates(result)
    return result


@app.get("/aceleration/{idMotor}")
async def get_aceleration_data(idMotor:str):
    aceleration_data = [d for d in vibration_data_list if d['idMotor'] == idMotor and d['medicion'] == 'aceleration']

    if not aceleration_data:
        raise HTTPException(status_code=404, detail=f"No se encontró información de velocidad para el motor {idMotor}")

    # Logica para calcular Rms
    rms = math.sqrt(sum([d['value']**2 for d in aceleration_data]) / len(aceleration_data))

    result = {
        "idMotor": idMotor,
        "rms": rms,
        "message": f"Se encontro que el valor de rms para el motor {idMotor} es de {rms}"
    }

    await send_updates(result)
    return result


@app.get("/temperature/{idMotor}")
async def get_temperature_data(idMotor:str):
    temperature_data = [d for d in vibration_data_list if d['idMotor'] == idMotor and d['medicion'] == 'temperature']

    if not temperature_data:
        raise HTTPException(status_code=404, detail=f"No se encontró información de velocidad para el motor {idMotor}")        

    ## Logica para el calculo de temperatura global
    promedio = sum([d['Value'] for d in temperature_data] / len(temperature_data))

    result = {
        "idMotor":idMotor,
        "promedio": promedio,
        "message":f"Se encontro que la temperatura promedio es {promedio}"
    }

    await send_updates(result)
    return result

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Leer el archivo CSV
        contents = await file.read()
        df = pd.read_csv(pd.compat.StringIO(contents.decode('utf-8')))
        
        # Suponiendo que tu CSV tiene columnas "idMotor", "medicion", "Value"
        data = df.to_dict(orient='records')
        
        # Separar los datos por tipo de medición
        velocity_data = [d for d in data if d['medicion'] == 'velocity']
        aceleration_data = [d for d in data if d['medicion'] == 'aceleration']
        temperature_data = [d for d in data if d['medicion'] == 'temperature']

        # Calcular resultados para velocidad
        if velocity_data:
            picos = [d for d in velocity_data if d['Value'] > 12]
            velocity_result = {
                "picos": picos,
                "message": f"Se encontraron {len(picos)} picos en la velocidad"
            }
            await send_updates(velocity_result)
        else:
            velocity_result = {"message": "No se encontraron datos de velocidad"}

        # Calcular resultados para aceleración
        if aceleration_data:
            rms = math.sqrt(sum([d['Value'] ** 2 for d in aceleration_data]) / len(aceleration_data))
            aceleration_result = {
                "rms": rms,
                "message": f"Se encontró que el valor de RMS para los datos de aceleración es de {rms}"
            }
            await send_updates(aceleration_result)
        else:
            aceleration_result = {"message": "No se encontraron datos de aceleración"}

        # Calcular resultados para temperatura
        if temperature_data:
            promedio = sum([d['Value'] for d in temperature_data]) / len(temperature_data)
            temperature_result = {
                "promedio": promedio,
                "message": f"Se encontró que la temperatura promedio es {promedio}"
            }
            await send_updates(temperature_result)
        else:
            temperature_result = {"message": "No se encontraron datos de temperatura"}

        return JSONResponse(content={
            "velocity": velocity_result,
            "aceleration": aceleration_result,
            "temperature": temperature_result
        })
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    start_consumer()
    uvicorn.run(app,host = "0.0.0.0",port=8000)