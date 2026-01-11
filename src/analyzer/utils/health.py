"""
Health check utilities to verify system setup and readiness.
"""

import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import settings

console = Console()


class HealthCheck:
    """System health checker."""

    def __init__(self):
        self.checks: list[tuple[str, bool, str]] = []

    def add_check(self, name: str, passed: bool, message: str = "") -> None:
        """Add a check result."""
        self.checks.append((name, passed, message))

    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        version = sys.version_info
        required = (3, 11)

        if version >= required:
            self.add_check(
                "Python Version",
                True,
                f"✓ Python {version.major}.{version.minor}.{version.micro}",
            )
            return True
        else:
            self.add_check(
                "Python Version",
                False,
                f"✗ Python {version.major}.{version.minor} (requires 3.11+)",
            )
            return False

    def check_environment_variables(self) -> bool:
        """Check if required environment variables are set."""
        checks = []

        # Check primary LLM API key
        if settings.primary_llm == "groq":
            if settings.groq_api_key:
                checks.append(("GROQ_API_KEY", True, "✓ Set"))
            else:
                checks.append(("GROQ_API_KEY", False, "✗ Not set"))

        elif settings.primary_llm == "anthropic":
            if settings.anthropic_api_key:
                checks.append(("ANTHROPIC_API_KEY", True, "✓ Set"))
            else:
                checks.append(("ANTHROPIC_API_KEY", False, "✗ Not set"))

        # Check environment
        checks.append(("ENVIRONMENT", True, f"✓ {settings.environment}"))
        checks.append(("LOG_LEVEL", True, f"✓ {settings.log_level}"))

        all_passed = all(passed for _, passed, _ in checks)

        for name, passed, msg in checks:
            self.add_check(f"Env: {name}", passed, msg)

        return all_passed

    def check_directories(self) -> bool:
        """Check if required directories exist."""
        directories = [
            ("data/memory", settings.memory_dir),
            ("data/logs", settings.log_dir),
            ("data/cache", settings.cache_dir),
            ("config", settings.config_dir),
            ("config/prompts", settings.prompts_dir),
        ]

        all_exist = True
        for name, path in directories:
            exists = path.exists() and path.is_dir()
            all_exist = all_exist and exists
            status = "✓ Exists" if exists else "✗ Missing"
            self.add_check(f"Directory: {name}", exists, status)

        return all_exist

    def check_dependencies(self) -> bool:
        """Check if key dependencies are installed."""
        dependencies = [
            ("groq", "Groq API client"),
            ("pydantic", "Data validation"),
            ("rich", "Terminal output"),
            ("typer", "CLI framework"),
            ("loguru", "Logging"),
            ("httpx", "HTTP client"),
        ]

        all_installed = True
        for package, description in dependencies:
            try:
                __import__(package)
                self.add_check(f"Package: {package}", True, f"✓ {description}")
            except ImportError:
                self.add_check(f"Package: {package}", False, f"✗ {description}")
                all_installed = False

        return all_installed

    def check_settings_load(self) -> bool:
        """Check if settings load correctly."""
        try:
            _ = settings.primary_llm
            _ = settings.max_iterations
            _ = settings.environment
            self.add_check("Settings", True, "✓ Loaded successfully")
            return True
        except Exception as e:
            self.add_check("Settings", False, f"✗ Error: {str(e)}")
            return False

    def check_llm_connectivity(self) -> bool:
        """Check if we can potentially connect to LLM (basic check)."""
        if settings.primary_llm == "groq":
            if settings.groq_api_key and settings.groq_api_key.startswith("gsk_"):
                self.add_check("LLM API Key", True, "✓ Key format valid")
                return True
            else:
                self.add_check("LLM API Key", False, "✗ Invalid key format")
                return False
        elif settings.primary_llm == "ollama":
            self.add_check("LLM", True, f"✓ Local Ollama ({settings.ollama_base_url})")
            return True
        else:
            self.add_check("LLM", True, f"✓ Using {settings.primary_llm}")
            return True

    def check_write_permissions(self) -> bool:
        """Check if we have write permissions to data directories."""
        test_dirs = [settings.log_dir, settings.cache_dir, settings.memory_dir]

        all_writable = True
        for directory in test_dirs:
            test_file = directory / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
                self.add_check(f"Write: {directory.name}", True, "✓ Writable")
            except Exception as e:
                self.add_check(f"Write: {directory.name}", False, f"✗ {str(e)}")
                all_writable = False

        return all_writable

    def run_all_checks(self) -> bool:
        """Run all health checks."""
        console.print("\n[bold cyan]🏥 Running System Health Checks...[/bold cyan]\n")

        results = [
            self.check_python_version(),
            self.check_dependencies(),
            self.check_settings_load(),
            self.check_environment_variables(),
            self.check_directories(),
            self.check_write_permissions(),
            self.check_llm_connectivity(),
        ]

        return all(results)

    def print_results(self) -> None:
        """Print health check results in a beautiful table."""
        table = Table(title="Health Check Results", show_header=True, header_style="bold magenta")
        table.add_column("Check", style="cyan", width=30)
        table.add_column("Status", width=10)
        table.add_column("Details", style="dim")

        for name, passed, message in self.checks:
            status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
            table.add_row(name, status, message)

        console.print(table)

        # Summary
        total = len(self.checks)
        passed = sum(1 for _, p, _ in self.checks if p)
        failed = total - passed

        if failed == 0:
            console.print(
                Panel(
                    f"[bold green]✅ All {total} checks passed! System is ready.[/bold green]",
                    title="Status",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold red]❌ {failed}/{total} checks failed. Please fix the issues above.[/bold red]",
                    title="Status",
                    border_style="red",
                )
            )

    def get_system_info(self) -> dict[str, str]:
        """Get system information."""
        return {
            "Python Version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "Platform": sys.platform,
            "Environment": settings.environment,
            "Primary LLM": settings.primary_llm,
            "Log Level": settings.log_level,
            "Max Iterations": str(settings.max_iterations),
            "Memory Enabled": str(settings.enable_memory),
        }

    def print_system_info(self) -> None:
        """Print system information."""
        info = self.get_system_info()

        table = Table(title="System Information", show_header=False)
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="green")

        for key, value in info.items():
            table.add_row(key, value)

        console.print("\n")
        console.print(table)


def run_health_check(verbose: bool = True) -> bool:
    """
    Run comprehensive health check.

    Args:
        verbose: Print detailed results

    Returns:
        True if all checks pass, False otherwise
    """
    checker = HealthCheck()
    all_passed = checker.run_all_checks()

    if verbose:
        checker.print_results()
        checker.print_system_info()

    return all_passed


def quick_check() -> bool:
    """Quick health check without verbose output."""
    checker = HealthCheck()
    return checker.run_all_checks()
