import React, {useEffect} from 'react'

function App(){
  useEffect(() => {
    const socket = new WebSocket('ws://192.168.0.6:8000/ws');

    socket.onopen = () => {
      console.log('Conectado al WebSocket')
    };

    socket.onmessage = (event) => {
      console.log('Mensaje recibido',event.data)
    };

    socket.onclose = () => {
      console.log('Conexion Websocket cerrada')
    };

    return () => {
      socket.close();
    };
 
  }, []);

  return (
    <div className="App">
      <h1>Conexion WebSocket React con FastApi desde React</h1>
    </div>
  );
}

export default App;