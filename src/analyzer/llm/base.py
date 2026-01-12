"""
Base interface for LLM clients.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in the conversation."""

    role: str = Field(..., description="Role: 'system', 'user', 'assistant', or 'tool'")
    content: str | None = Field(None, description="Message content")
    tool_call_id: str | None = Field(None, description="ID of tool call (for tool responses)")
    name: str | None = Field(None, description="Tool name (for tool responses)")
    tool_calls: list[dict] | None = Field(None, description="Tool calls (for assistant messages)")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API calls."""
        data: dict[str, Any] = {"role": self.role}

        # Content can be None for assistant messages with tool_calls
        if self.content is not None:
            data["content"] = self.content

        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
        if self.name:
            data["name"] = self.name
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        return data


class ToolCall(BaseModel):
    """A tool call request from the LLM."""

    id: str = Field(..., description="Unique tool call ID")
    name: str = Field(..., description="Tool name to execute")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


class LLMResponse(BaseModel):
    """Response from the LLM."""

    content: str | None = Field(None, description="Text response from LLM")
    tool_calls: list[ToolCall] = Field(
        default_factory=list, description="Tool calls requested by LLM"
    )
    finish_reason: str | None = Field(None, description="Why the LLM stopped")
    raw_response: dict | None = Field(None, description="Raw API response")

    def has_tool_calls(self) -> bool:
        """Check if LLM wants to use tools."""
        return len(self.tool_calls) > 0

    def is_final(self) -> bool:
        """Check if this is a final response (no more tool calls)."""
        return not self.has_tool_calls() and self.content is not None


class BaseLLM(ABC):
    """
    Abstract base class for LLM clients.

    All LLM implementations (Groq, Ollama, Claude, etc.)
    must implement this interface.
    """

    @abstractmethod
    def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """
        Send a chat request to the LLM.

        Args:
            messages: Conversation history
            tools: Available tools (function calling schemas)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            LLM response with content or tool calls

        Raises:
            LLMConnectionError: If connection fails
            LLMResponseError: If response is invalid
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the model being used."""
        pass

    def supports_tool_calling(self) -> bool:
        """Check if this LLM supports tool/function calling."""
        return True

    def get_token_limit(self) -> int:
        """Get context window size in tokens."""
        return 4096  # Default, override in subclasses
