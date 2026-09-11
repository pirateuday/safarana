from typing import Callable, Any, Dict, List, Optional
import inspect

class Tool:
    def __init__(self, name: str, description: str, func: Callable, parameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters or self._extract_parameters(func)

    def _extract_parameters(self, func: Callable) -> Dict[str, Any]:
        sig = inspect.signature(func)
        params = {}
        for param_name, param in sig.parameters.items():
            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"
            elif param.annotation == list or getattr(param.annotation, "__origin__", None) == list:
                param_type = "array"
            elif param.annotation == dict or getattr(param.annotation, "__origin__", None) == dict:
                param_type = "object"

            params[param_name] = {
                "type": param_type,
                "required": param.default == inspect.Parameter.empty,
                "default": None if param.default == inspect.Parameter.empty else param.default
            }
        return params

    def execute(self, **kwargs) -> Any:
        return self.func(**kwargs)

    def to_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class ToolRegistry:
    _instance = None

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    @classmethod
    def get_instance(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, name: Optional[str] = None, description: Optional[str] = None):
        """Decorator to register a function as a Tool."""
        def decorator(func: Callable):
            tool_name = name or func.__name__
            tool_desc = description or (func.__doc__ or "No description provided").strip()
            tool = Tool(tool_name, tool_desc, func)
            self._tools[tool_name] = tool
            return func
        return decorator

    def register_tool(self, tool: Tool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_schema() for tool in self._tools.values()]

    def execute(self, name: str, **kwargs) -> Any:
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry.")
        return tool.execute(**kwargs)

# Global registry instance
registry = ToolRegistry.get_instance()
tool = registry.register
