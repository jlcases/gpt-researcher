from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import logging

from api.ws_manager import process_websocket_data

# Configuración de logging para debugging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
app.mount("/site", StaticFiles(directory="client"), name="site")
app.mount("/static", StaticFiles(directory="client/static"), name="static")

@app.on_event("startup")
def startup_event():
    if not os.path.isdir("outputs"):
        os.makedirs("outputs")
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

templates = Jinja2Templates(directory="client")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request, "report": None})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logging.debug("Iniciando conexión WebSocket...")
    await websocket.accept()
    data = await websocket.receive_text()
    logging.debug(f"Datos recibidos por WebSocket: {data}")
    await process_websocket_data(websocket, data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)





