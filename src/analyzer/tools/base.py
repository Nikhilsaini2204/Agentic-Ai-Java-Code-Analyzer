"""
Base class for all tools that the agent can use.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Definition of a tool parameter."""

    name: str
    type: str  # "string", "integer", "boolean", etc.
    description: str
    required: bool = True
    default: Any = None


class ToolDefinition(BaseModel):
    """Tool definition for LLM function calling."""

    name: str
    description: str
    parameters: dict[str, ToolParameter] = Field(default_factory=dict)

    def to_function_schema(self) -> dict[str, Any]:
        """
        Convert to OpenAI/Groq function calling schema.

        Returns:
            Schema dict compatible with LLM APIs
        """
        properties = {}
        required = []

        for param_name, param in self.parameters.items():
            properties[param_name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.default is not None:
                properties[param_name]["default"] = param.default

            if param.required:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


class BaseTool(ABC):
    """
    Abstract base class for all tools.

    Every tool must:
    1. Have a unique name
    2. Provide a description (for LLM to understand when to use it)
    3. Define its parameters
    4. Implement the execute method
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name (snake_case)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """What this tool does (for LLM to decide when to use it)."""
        pass

    @abstractmethod
    def get_parameters(self) -> dict[str, ToolParameter]:
        """Define the parameters this tool accepts."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool parameters

        Returns:
            Result as string (for LLM to read and understand)

        Raises:
            ToolExecutionError: If execution fails
        """
        pass

    def get_definition(self) -> ToolDefinition:
        """Get tool definition for LLM."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.get_parameters(),
        )

    def to_function_schema(self) -> dict[str, Any]:
        """Convert to LLM function calling schema."""
        return self.get_definition().to_function_schema()

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"
