"""
Custom exceptions for the analyzer.
"""


class AnalyzerError(Exception):
    """Base exception for all analyzer errors."""

    pass


class LLMError(AnalyzerError):
    """Error related to LLM operations."""

    pass


class LLMConnectionError(LLMError):
    """Failed to connect to LLM API."""

    pass


class LLMResponseError(LLMError):
    """LLM returned invalid or unexpected response."""

    pass


class ToolError(AnalyzerError):
    """Error related to tool execution."""

    pass


class ToolNotFoundError(ToolError):
    """Requested tool doesn't exist."""

    pass


class ToolExecutionError(ToolError):
    """Tool execution failed."""

    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' failed: {message}")


class AgentError(AnalyzerError):
    """Error in agent operations."""

    pass


class AgentTimeoutError(AgentError):
    """Agent exceeded maximum iterations."""

    pass


class ConfigurationError(AnalyzerError):
    """Configuration is invalid or missing."""

    pass


class FileAnalysisError(AnalyzerError):
    """Error analyzing a file."""

    def __init__(self, file_path: str, message: str):
        self.file_path = file_path
        super().__init__(f"Failed to analyze '{file_path}': {message}")
