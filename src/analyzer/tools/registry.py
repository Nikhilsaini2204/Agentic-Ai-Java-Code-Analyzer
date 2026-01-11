"""
Tool registry - manages all available tools for the agent.
"""


from loguru import logger

from analyzer.tools.base import BaseTool
from analyzer.utils.exceptions import ToolNotFoundError


class ToolRegistry:
    """
    Central registry for all tools available to the agent.

    The agent queries this registry to:
    - Discover available tools
    - Get tool schemas for LLM
    - Execute tools by name
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        logger.info("Tool registry initialized")

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance to register
        """
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' already registered, overwriting")

        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def unregister(self, tool_name: str) -> None:
        """
        Unregister a tool.

        Args:
            tool_name: Name of tool to unregister
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")

    def get_tool(self, tool_name: str) -> BaseTool:
        """
        Get a tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool instance

        Raises:
            ToolNotFoundError: If tool doesn't exist
        """
        if tool_name not in self._tools:
            available = ", ".join(self._tools.keys())
            raise ToolNotFoundError(f"Tool '{tool_name}' not found. Available tools: {available}")

        return self._tools[tool_name]

    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools

    def get_all_tools(self) -> list[BaseTool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def get_tool_names(self) -> list[str]:
        """Get names of all registered tools."""
        return list(self._tools.keys())

    def get_tool_schemas(self) -> list[dict]:
        """
        Get function schemas for all tools (for LLM).

        Returns:
            List of tool schemas in OpenAI/Groq function calling format
        """
        return [tool.to_function_schema() for tool in self._tools.values()]

    def execute_tool(self, tool_name: str, **parameters) -> str:
        """
        Execute a tool with given parameters.

        Args:
            tool_name: Name of the tool to execute
            **parameters: Tool parameters

        Returns:
            Tool execution result

        Raises:
            ToolNotFoundError: If tool doesn't exist
            ToolExecutionError: If tool execution fails
        """
        tool = self.get_tool(tool_name)
        logger.info(f"Executing tool: {tool_name} with params: {parameters}")

        result = tool.execute(**parameters)

        logger.debug(
            f"Tool '{tool_name}' executed successfully, " f"result length: {len(result)} chars"
        )

        return result

    def get_summary(self) -> str:
        """Get a summary of registered tools."""
        if not self._tools:
            return "No tools registered"

        summary = [f"Registered tools ({len(self._tools)}):"]
        for tool in self._tools.values():
            summary.append(f"  - {tool.name}: {tool.description}")

        return "\n".join(summary)

    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)

    def __repr__(self) -> str:
        return f"<ToolRegistry: {len(self._tools)} tools>"


# Global registry instance (singleton pattern)
_global_registry: ToolRegistry | None = None


def get_registry() -> ToolRegistry:
    """
    Get the global tool registry.

    Returns:
        Global ToolRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def register_default_tools() -> ToolRegistry:
    """
    Register all default tools.

    Returns:
        Registry with all default tools registered
    """
    from analyzer.tools.code.complexity import ComplexityAnalysisTool
    from analyzer.tools.code.reader import ReadFileTool
    from analyzer.tools.code.static_analyzer import StaticAnalysisTool

    registry = get_registry()

    # Register code analysis tools
    registry.register(ReadFileTool())
    registry.register(StaticAnalysisTool())
    registry.register(ComplexityAnalysisTool())

    logger.info(f"Registered {len(registry)} default tools")
    return registry
