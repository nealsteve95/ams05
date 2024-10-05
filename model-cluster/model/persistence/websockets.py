from fastapi import WebSocket,WebSocketDisconnect
from fastapi import APIRouter

clients = []

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            # Espera los mensajes desde el cliente
            data = await websocket.receive_text()
            print(f"Mensaje recibido desde el cliente: {data}")
            # Enviar datos de prueba al cliente
            await websocket.send_text("Hola desde Fastapi por websockets")
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Cliente desconectado")

async def send_updates(data : dict):
    for client in clients:
        await client.send_text(f"Actualizacion de datos {data}")

