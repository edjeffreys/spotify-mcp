from typing import Any

import mcp.types as types
from pydantic import BaseModel, PrivateAttr

from ..spotify_api import Client

class ToolModel(BaseModel):
    _spotify_client: Client = PrivateAttr()

    class Schema(BaseModel):
        pass

    def __init__(self, spotify_client: Client) -> None:
        super().__init__()
        self._spotify_client = spotify_client

    @classmethod
    def as_tool(cls):
        return types.Tool(
            name="Spotify" + cls.__name__,
            description=cls.__doc__,
            inputSchema=cls.Schema.model_json_schema()
        )

    def execute(self, method_name: str, *args, **kwargs) -> Any:
        if not hasattr(self, method_name):
            raise AttributeError(f"Method '{method_name}' not found in {self.__class__.__name__}")
        method = getattr(self, method_name)
        if not callable(method):
            raise ValueError(f"'{method_name}' is not a callable method")
        return method(*args, **kwargs)