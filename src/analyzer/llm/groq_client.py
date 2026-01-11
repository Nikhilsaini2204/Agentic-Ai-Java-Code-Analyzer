"""
Groq LLM client implementation.
"""


from groq import Groq
from loguru import logger

from analyzer.llm.base import BaseLLM, LLMResponse, Message, ToolCall
from analyzer.utils.exceptions import LLMConnectionError, LLMResponseError


class GroqLLMClient(BaseLLM):
    """
    LLM client for Groq API (uses Llama 3.3 70B).

    Groq provides free, fast inference for open models.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """
        Initialize Groq client.

        Args:
            api_key: Groq API key
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
        """
        self.api_key = api_key
        self.model = model
        self.default_temperature = temperature
        self.default_max_tokens = max_tokens

        try:
            self.client = Groq(api_key=api_key)
            logger.info(f"Groq client initialized with model: {model}")
        except Exception as e:
            raise LLMConnectionError(f"Failed to initialize Groq client: {str(e)}")

    def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """
        Send chat request to Groq.

        Args:
            messages: Conversation history
            tools: Available tools
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            LLM response
        """
        try:
            # Convert messages to API format
            api_messages = [msg.to_dict() for msg in messages]

            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": api_messages,
                "temperature": temperature or self.default_temperature,
                "max_tokens": max_tokens or self.default_max_tokens,
            }

            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"

            logger.debug(
                f"Sending request to Groq: {len(api_messages)} messages, "
                f"{len(tools) if tools else 0} tools"
            )

            # Make API call
            response = self.client.chat.completions.create(**request_params)

            # Parse response
            return self._parse_response(response)

        except Exception as e:
            logger.error(f"Groq API call failed: {str(e)}")
            raise LLMConnectionError(f"Groq API error: {str(e)}")

    def _parse_response(self, response) -> LLMResponse:
        """
        Parse Groq API response.

        Args:
            response: Raw API response

        Returns:
            Parsed LLMResponse
        """
        try:
            choice = response.choices[0]
            message = choice.message

            # Check for tool calls
            tool_calls = []
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    # Parse function arguments (they come as JSON string)
                    import json

                    parameters = json.loads(tool_call.function.arguments)

                    tool_calls.append(
                        ToolCall(
                            id=tool_call.id,
                            name=tool_call.function.name,
                            parameters=parameters,
                        )
                    )

                logger.info(f"LLM requested {len(tool_calls)} tool call(s)")

            # Get text content
            content = message.content if hasattr(message, "content") else None

            # Get finish reason
            finish_reason = choice.finish_reason if hasattr(choice, "finish_reason") else None

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
                raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
            )

        except Exception as e:
            logger.error(f"Failed to parse Groq response: {str(e)}")
            raise LLMResponseError(f"Invalid response from Groq: {str(e)}")

    def get_model_name(self) -> str:
        """Get model name."""
        return self.model

    def supports_tool_calling(self) -> bool:
        """Groq/Llama 3.3 supports tool calling."""
        return True

    def get_token_limit(self) -> int:
        """Llama 3.3 70B context window."""
        return 128000  # 128K tokens

    def __repr__(self) -> str:
        return f"<GroqLLMClient: {self.model}>"
