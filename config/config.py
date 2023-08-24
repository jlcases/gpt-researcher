import os

import openai
from colorama import Fore
from dotenv import load_dotenv

from config.singleton import Singleton

load_dotenv(verbose=True)


class Config(metaclass=Singleton):
    """
    Configuration class to store the state of bools for different scripts access.
    """

    def __init__(self) -> None:
        """Initialize the Config class"""
        self.debug_mode = False
        self.allow_downloads = False

        self.selenium_web_browser = os.getenv("USE_WEB_BROWSER", "chrome")
        self.llm_provider = os.getenv("LLM_PROVIDER", "ChatOpenAI")
        self.fast_llm_model = os.getenv("FAST_LLM_MODEL", "gpt-3.5-turbo-16k")
        self.smart_llm_model = os.getenv("SMART_LLM_MODEL", "gpt-4")
        self.fast_token_limit = int(os.getenv("FAST_TOKEN_LIMIT", 4000))
        self.smart_token_limit = int(os.getenv("SMART_TOKEN_LIMIT", 8000))
        self.browse_chunk_max_length = int(os.getenv("BROWSE_CHUNK_MAX_LENGTH", 8192))

        self.openai_api_key = None
        self.websocket_openai_api_key = None  # Nueva variable para almacenar la clave de API de websocket
        self.temperature = float(os.getenv("TEMPERATURE", "1"))

        self.user_agent = os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        )

        self.memory_backend = os.getenv("MEMORY_BACKEND", "local")

    ...

    def set_websocket_openai_api_key(self, key: str) -> None:
        """Set the OpenAI API key received from websocket."""
        self.websocket_openai_api_key = key

    def get_openai_api_key(self) -> str:
        """Get the OpenAI API key value."""
        if self.websocket_openai_api_key:
            return self.websocket_openai_api_key
        elif self.openai_api_key:
            return self.openai_api_key
        else:
            raise ValueError("OpenAI API key has not been set.")

    ...


def check_openai_api_key(api_key: str) -> None:
    """Verifica la clave API de OpenAI proporcionada."""
    if not api_key:
        error_message = (
            "Por favor, proporciona tu clave API de OpenAI.\n"
            "Puedes obtener tu clave en https://platform.openai.com/account/api-keys"
        )
        raise ValueError(error_message)


# Usar esta función cuando necesites la clave API en tu código
def get_openai_api_key() -> str:
    config = Config()
    return config.get_openai_api_key()


