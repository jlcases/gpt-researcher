import json
import openai
from config.config import Config
from agent.llm_utils import choose_agent
from agent.run import WebSocketManager

manager = WebSocketManager()

async def verify_api_key(api_key):
    config = Config()  # Obtén la instancia del objeto de configuración
    openai.api_key = api_key
    try:
        # Hacer una llamada de prueba a la API
        response = openai.Completion.create(engine="davinci", prompt="test", max_tokens=5)
        return True, "La clave API es válida"
    except openai.error.OpenAIError as e:
        # Si el error es debido a una clave API incorrecta, devolvemos un mensaje personalizado
        if "Incorrect API key provided" in str(e):
            return False, "La clave API proporcionada es incorrecta. Puedes encontrar tu clave API en https://platform.openai.com/account/api-keys."
        return False, "Se produjo un error: " + str(e)
    except Exception as e:
        return False, "Se produjo un error: " + str(e)


async def process_websocket_data(websocket, data):
    config = Config()  # Obtén la instancia del objeto de configuración al principio
    
    if data.startswith("start"):
        json_data = json.loads(data[6:])
        openai_api_key = json_data.get("openai_api_key")
        print(f"Received OpenAI API key: {openai_api_key}")
        is_valid, message = await verify_api_key(openai_api_key)
        if not is_valid:
            await websocket.send_json({"type": "error", "output": message})
            return
        # Guarda la clave API en el objeto de configuración
        config.set_websocket_openai_api_key(openai_api_key)

        # Una vez verificada la API, procesar el resto de los datos
        task = json_data.get("task")
        report_type = json_data.get("report_type")
        agent = json_data.get("agent")
        language = json_data.get("language")

        if agent == "Auto Agent":
            agent_dict = choose_agent(task)
            agent = agent_dict.get("agent")
            agent_role_prompt = agent_dict.get("agent_role_prompt")
        else:
            agent_role_prompt = None

        await websocket.send_json({"type": "logs", "output": f"¡Dulai a tu servicio!<br> Empiezo a trabajar por ti.<br>☕ Tómate un café.Inicio un agente: {agent}"})

        if task and report_type and agent:
            print(f"About to call start_streaming with key: {openai_api_key}")
            try:
                await manager.start_streaming(task, report_type, agent, agent_role_prompt, language, openai_api_key, websocket)
                await websocket.send_json({"type": "success", "output": "All data processed successfully."})
            except Exception as e:
                await websocket.send_json({"type": "error", "output": f"Error: {str(e)}"})
        else:
            await websocket.send_json({"type": "error", "output": "Error: not enough parameters provided."})
    else:
        await websocket.send_json({"type": "error", "output": "Invalid request."})

