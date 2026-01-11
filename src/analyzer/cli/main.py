"""
Command-line interface for the Java Code Analyzer.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from analyzer.core.agent import CodeAnalysisAgent
from analyzer.llm.groq_client import GroqLLMClient
from analyzer.tools.registry import register_default_tools
from analyzer.utils.logger import setup_logger
from config.settings import settings

app = typer.Typer(
    name="java-analyzer",
    help="Agentic AI system for autonomous Java code analysis",
    add_completion=False,
)
console = Console()


@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="Path to Java file to analyze"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed agent execution"),
    max_iterations: int | None = typer.Option(
        None, "--max-iterations", "-m", help="Maximum agent loop iterations"
    ),
):
    """
    Analyze a Java file using autonomous AI agent.

    Example:
        java-analyzer analyze MyCode.java
        java-analyzer analyze src/Main.java --verbose
    """
    # Setup logging
    setup_logger()

    # Display banner
    if verbose:
        console.print(
            Panel.fit(
                "🤖 [bold cyan]Java Code Analyzer[/bold cyan]\n"
                "Agentic AI System for Code Analysis",
                border_style="cyan",
            )
        )
        console.print(f"\n📁 File: [bold]{file_path}[/bold]")
        console.print(f"🔧 LLM: {settings.primary_llm} ({settings.groq_model})")
        console.print(f"🎯 Max iterations: {max_iterations or settings.max_iterations}\n")

    # Validate file exists
    path = Path(file_path)
    if not path.exists():
        console.print(f"[red]✗ Error: File not found: {file_path}[/red]")
        raise typer.Exit(1)

    if not path.is_file():
        console.print(f"[red]✗ Error: Path is not a file: {file_path}[/red]")
        raise typer.Exit(1)

    if path.suffix.lower() != ".java":
        console.print(f"[red]✗ Error: Not a Java file: {file_path}[/red]")
        raise typer.Exit(1)

    try:
        # Initialize LLM
        if verbose:
            console.print("[cyan]Initializing LLM client...[/cyan]")

        llm = GroqLLMClient(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.groq_temperature,
            max_tokens=settings.groq_max_tokens,
        )

        # Register tools
        if verbose:
            console.print("[cyan]Loading analysis tools...[/cyan]")

        tool_registry = register_default_tools()

        if verbose:
            console.print(f"[green]✓ Loaded {len(tool_registry)} tools[/green]\n")
            for tool in tool_registry.get_all_tools():
                console.print(f"  • {tool.name}: {tool.description[:60]}...")

        # Create agent
        agent = CodeAnalysisAgent(
            llm=llm,
            tool_registry=tool_registry,
            max_iterations=max_iterations or settings.max_iterations,
            verbose=verbose,
        )

        # Run analysis
        console.print("\n" + "=" * 70)

        result = agent.analyze_file(str(path.absolute()))

        # Display result
        console.print("\n" + "=" * 70)
        console.print(
            Panel.fit(
                "📊 [bold green]Analysis Complete[/bold green]",
                border_style="green",
            )
        )
        console.print("\n")

        # Render result as markdown if it contains markdown syntax
        if "```" in result or "#" in result[:50]:
            console.print(Markdown(result))
        else:
            console.print(result)

        console.print("\n" + "=" * 70)

    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        raise typer.Exit(130)

    except Exception as e:
        console.print(f"\n[red]✗ Analysis failed: {str(e)}[/red]")
        if verbose:
            import traceback

            console.print("\n[dim]" + traceback.format_exc() + "[/dim]")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from analyzer import __version__

    console.print(f"Java Code Analyzer version {__version__}")
    console.print(f"LLM: {settings.primary_llm}")
    console.print(f"Environment: {settings.environment}")


@app.command()
def tools():
    """List available analysis tools."""
    setup_logger()

    console.print(
        Panel.fit(
            "🔧 [bold]Available Analysis Tools[/bold]",
            border_style="cyan",
        )
    )

    tool_registry = register_default_tools()

    for tool in tool_registry.get_all_tools():
        console.print(f"\n[bold cyan]{tool.name}[/bold cyan]")
        console.print(f"  {tool.description}")

        params = tool.get_parameters()
        if params:
            console.print("  [dim]Parameters:[/dim]")
            for param_name, param in params.items():
                required = "[red]*[/red]" if param.required else ""
                console.print(f"    • {param_name}{required}: {param.description}")


@app.command()
def config():
    """Show current configuration."""
    console.print(
        Panel.fit(
            "⚙️  [bold]Current Configuration[/bold]",
            border_style="cyan",
        )
    )

    console.print(f"\n[bold]Environment:[/bold] {settings.environment}")
    console.print(f"[bold]Log Level:[/bold] {settings.log_level}")
    console.print("\n[bold]LLM Settings:[/bold]")
    console.print(f"  Primary LLM: {settings.primary_llm}")
    console.print(f"  Model: {settings.groq_model}")
    console.print(f"  Temperature: {settings.groq_temperature}")
    console.print(f"  Max Tokens: {settings.groq_max_tokens}")
    console.print("\n[bold]Agent Settings:[/bold]")
    console.print(f"  Max Iterations: {settings.max_iterations}")
    console.print(f"  Timeout: {settings.timeout_seconds}s")
    console.print("\n[bold]Features:[/bold]")
    console.print(f"  Memory: {'Enabled' if settings.enable_memory else 'Disabled'}")
    console.print(f"  Caching: {'Enabled' if settings.cache_llm_responses else 'Disabled'}")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
