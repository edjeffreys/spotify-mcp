from typing import TypeVar

from .tool_model import ToolModel


ToolModelBase = TypeVar("ToolModelBase", bound=ToolModel)
