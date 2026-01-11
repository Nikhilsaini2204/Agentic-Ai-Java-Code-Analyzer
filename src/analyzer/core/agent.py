"""
The core agent - autonomous code analysis AI.
"""


from loguru import logger
from rich.console import Console
from rich.panel import Panel

from analyzer.llm.base import BaseLLM, Message
from analyzer.tools.registry import ToolRegistry
from analyzer.utils.exceptions import AgentError, AgentTimeoutError, ToolExecutionError

console = Console()


class CodeAnalysisAgent:
    """
    Autonomous agent for Java code analysis.

    The agent:
    1. Receives a goal (e.g., "analyze this file")
    2. Decides which tools to use and when
    3. Chains multiple tools together
    4. Synthesizes findings
    5. Provides actionable recommendations

    This is TRUE agentic AI - the LLM makes all decisions.
    """

    # System prompt that defines the agent's behavior
    SYSTEM_PROMPT = """You are an expert Java code analysis agent. Your goal is to thoroughly analyze Java code for quality, security, and best practices.

You have access to tools that help you analyze code. You should:

1. **Always start by reading the file** to understand what you're analyzing
2. **Think strategically** about what analysis is most important based on what the code does
3. **Use multiple tools** to get a comprehensive view
4. **Synthesize findings** into clear, actionable recommendations
5. **Prioritize issues** by severity (security > bugs > complexity > style)

Process for analyzing a file:
1. Use `read_file` to examine the code
2. Based on what you see, decide which analysis tools are most relevant:
   - `static_analysis` for code quality issues
   - `complexity_analysis` for code metrics
3. After using tools, provide a final comprehensive report

Important guidelines:
- Always read the file first before any analysis
- Use tools in a logical order
- After using all necessary tools, provide a final summary
- When you're done analyzing, clearly state your conclusions and recommendations
- Be thorough but efficient - use only the tools that add value

Think step by step and explain your reasoning as you work."""

    def __init__(
        self,
        llm: BaseLLM,
        tool_registry: ToolRegistry,
        max_iterations: int = 15,
        verbose: bool = False,
    ):
        """
        Initialize the agent.

        Args:
            llm: LLM client for reasoning
            tool_registry: Available tools
            max_iterations: Maximum agent loop iterations
            verbose: Print detailed execution logs
        """
        self.llm = llm
        self.tool_registry = tool_registry
        self.max_iterations = max_iterations
        self.verbose = verbose

        # Conversation history
        self.messages: list[Message] = []

        # Add system prompt
        self.messages.append(Message(role="system", content=self.SYSTEM_PROMPT))

        logger.info(
            f"Agent initialized with {len(tool_registry)} tools, "
            f"max {max_iterations} iterations"
        )

    def analyze_file(self, file_path: str) -> str:
        """
        Analyze a Java file autonomously.

        This is the main entry point. The agent will:
        - Read the file
        - Decide which analyses to run
        - Execute tools
        - Synthesize a final report

        Args:
            file_path: Path to Java file to analyze

        Returns:
            Final analysis report

        Raises:
            AgentTimeoutError: If max iterations exceeded
            AgentError: If analysis fails
        """
        logger.info(f"Agent starting analysis of: {file_path}")

        if self.verbose:
            console.print(
                Panel(
                    f"🤖 Starting autonomous analysis of:\n[bold]{file_path}[/bold]",
                    title="Agent Started",
                    border_style="cyan",
                )
            )

        # Add user request
        user_message = (
            f"Analyze the Java file at path: {file_path}\n\n"
            f"Perform a thorough analysis and provide actionable recommendations."
        )
        self.messages.append(Message(role="user", content=user_message))

        # Run agent loop
        try:
            final_report = self._agent_loop()
            logger.info("Agent analysis complete")
            return final_report
        except Exception as e:
            logger.error(f"Agent analysis failed: {str(e)}")
            raise AgentError(f"Analysis failed: {str(e)}")

    def _agent_loop(self) -> str:
        """
        The core agent loop: observe → think → decide → act.

        This loop continues until:
        - Agent provides final answer (no more tool calls)
        - Max iterations reached

        Returns:
            Final analysis report
        """
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            if self.verbose:
                console.print(
                    f"\n[bold cyan]🔄 Iteration {iteration}/{self.max_iterations}[/bold cyan]"
                )

            logger.debug(f"Agent loop iteration {iteration}")

            # Get tool schemas for LLM
            tool_schemas = self.tool_registry.get_tool_schemas()

            # Ask LLM what to do next
            try:
                response = self.llm.chat(
                    messages=self.messages,
                    tools=tool_schemas if tool_schemas else None,
                )
            except Exception as e:
                raise AgentError(f"LLM call failed: {str(e)}")

            # Check if LLM wants to use tools
            if response.has_tool_calls():
                # Execute tools and continue loop
                self._handle_tool_calls(response.tool_calls)

            else:
                # LLM provided final answer
                if response.content:
                    if self.verbose:
                        console.print(
                            Panel(
                                "✅ Agent has completed analysis",
                                border_style="green",
                            )
                        )

                    # Add to history
                    self.messages.append(Message(role="assistant", content=response.content))

                    logger.info(f"Agent finished after {iteration} iterations")
                    return response.content
                else:
                    # No content and no tool calls - something wrong
                    raise AgentError("LLM returned no content and no tool calls")

        # Reached max iterations without final answer
        logger.warning(f"Agent reached max iterations ({self.max_iterations})")

        if self.verbose:
            console.print(
                Panel(
                    "⚠️  Reached maximum iterations, requesting final summary",
                    border_style="yellow",
                )
            )

        # Request final summary
        self.messages.append(
            Message(
                role="user",
                content="Please provide a final summary of your analysis now based on what you've learned so far.",
            )
        )

        try:
            response = self.llm.chat(messages=self.messages, tools=None)
            if response.content:
                return response.content
            else:
                raise AgentTimeoutError(
                    f"Agent exceeded {self.max_iterations} iterations without completing analysis"
                )
        except Exception as e:
            raise AgentError(f"Failed to get final summary: {str(e)}")

    def _handle_tool_calls(self, tool_calls: list) -> None:
        """
        Execute tools requested by the agent.

        Args:
            tool_calls: List of ToolCall objects
        """
        for tool_call in tool_calls:
            tool_name = tool_call.name
            parameters = tool_call.parameters

            if self.verbose:
                console.print(
                    f"🔧 [bold]Agent decided to use:[/bold] {tool_name}",
                    style="cyan",
                )
                if parameters:
                    console.print(f"   Parameters: {parameters}", style="dim")

            logger.info(f"Executing tool: {tool_name} with params: {parameters}")

            # Execute tool
            try:
                result = self.tool_registry.execute_tool(tool_name, **parameters)

                if self.verbose:
                    # Show preview of result
                    preview = result[:200] + "..." if len(result) > 200 else result
                    console.print(f"   ✓ Result preview: {preview}", style="dim")

                logger.debug(f"Tool {tool_name} executed successfully")

            except ToolExecutionError as e:
                # Tool failed - inform the agent
                result = f"ERROR: {str(e)}"
                logger.warning(f"Tool {tool_name} failed: {str(e)}")

                if self.verbose:
                    console.print(f"   ✗ Tool failed: {str(e)}", style="red")

            # Add tool result to conversation
            self.messages.append(
                Message(
                    role="tool",
                    content=result,
                    tool_call_id=tool_call.id,
                    name=tool_name,
                )
            )

    def get_conversation_history(self) -> list[Message]:
        """Get the conversation history."""
        return self.messages.copy()

    def reset(self) -> None:
        """Reset agent to initial state."""
        self.messages = [Message(role="system", content=self.SYSTEM_PROMPT)]
        logger.info("Agent reset")

    def __repr__(self) -> str:
        return (
            f"<CodeAnalysisAgent: {self.llm.get_model_name()}, " f"{len(self.tool_registry)} tools>"
        )
