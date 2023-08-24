from __future__ import annotations

# Importaciones estándar
import json
import logging

# Importaciones de terceros
from fastapi import WebSocket
from colorama import Fore, Style
from openai.error import APIError, RateLimitError

# Importaciones locales
from config.config import get_openai_api_key, Config
from langchain.adapters import openai as lc_openai
from agent.prompts import auto_agent_instructions

from typing import Optional

# Configuración inicial
CFG = Config()


def create_chat_completion(
    messages: list,
    model: Optional[str] = None,
    temperature: float = CFG.temperature,
    max_tokens: Optional[int] = None,
    stream: Optional[bool] = False,
    websocket: WebSocket | None = None,
    openai_api_key: Optional[str] = None
) -> str:
    """Create a chat completion using the OpenAI API."""

    # Validaciones
    if model is None:
        raise ValueError("Model cannot be None")
    if max_tokens is not None and max_tokens > 8001:
        raise ValueError(f"Max tokens cannot be more than 8001, but got {max_tokens}")
    if stream and websocket is None:
        raise ValueError("Websocket cannot be None when stream is True")

    # Intenta obtener una respuesta
    for attempt in range(10):  # maximum of 10 attempts
        response = send_chat_completion_request(
            messages, model, temperature, max_tokens, stream, websocket, openai_api_key
        )
        return response

    logging.error("Failed to get response from OpenAI API")
    raise RuntimeError("Failed to get response from OpenAI API")


def send_chat_completion_request(
    messages, model, temperature, max_tokens, stream, websocket, openai_api_key: Optional[str] = None
):
    """Envía una solicitud de completado de chat a la API de OpenAI."""
    
    local_openai_api_key = openai_api_key or get_openai_api_key()

    if not stream:
        result = lc_openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            provider=CFG.llm_provider,
            openai_api_key=local_openai_api_key
        )
        return result["choices"][0]["message"]["content"]
    else:
        return stream_response(model, messages, temperature, max_tokens, websocket, local_openai_api_key)


async def stream_response(model, messages, temperature, max_tokens, websocket, openai_api_key: Optional[str] = None):
    """Stream the response from OpenAI in chunks."""
    
    paragraph = ""
    response = ""
    print(f"streaming response...")

    for chunk in lc_openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            provider=CFG.llm_provider,
            stream=True,
            openai_api_key=openai_api_key
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            response += content
            paragraph += content
            if "\n" in paragraph:
                await websocket.send_json({"type": "report", "output": paragraph})
                paragraph = ""

    print(f"streaming response complete")
    return response


def choose_agent(task: str) -> str:
    """Determines what agent should be used based on the task."""
    
    try:
        response = create_chat_completion(
            model=CFG.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{auto_agent_instructions()}"},
                {"role": "user", "content": f"task: {task}"}],
            temperature=0,
        )

        return json.loads(response)
    except Exception as e:
        print(f"{Fore.RED}Error in choose_agent: {e}{Style.RESET_ALL}")
        return {
            "agent": "Default Agent",
            "agent_role_prompt": "You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured reports on given text."
        }

