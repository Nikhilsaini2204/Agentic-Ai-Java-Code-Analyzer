"""
Tool for reading Java source files.
"""

from pathlib import Path

from analyzer.tools.base import BaseTool, ToolParameter
from analyzer.utils.exceptions import ToolExecutionError


class ReadFileTool(BaseTool):
    """
    Reads and returns the contents of a Java source file.

    The agent uses this tool to examine code before analysis.
    """

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return (
            "Reads the contents of a Java source file. "
            "Use this first to understand what code you're analyzing. "
            "Returns the file contents with line numbers and basic statistics."
        )

    def get_parameters(self) -> dict[str, ToolParameter]:
        return {
            "file_path": ToolParameter(
                name="file_path",
                type="string",
                description="Path to the Java file to read (e.g., 'src/Main.java')",
                required=True,
            )
        }

    def execute(self, file_path: str, **kwargs) -> str:
        """
        Read a Java file and return its contents.

        Args:
            file_path: Path to the Java file

        Returns:
            Formatted string with file contents and metadata
        """
        try:
            path = Path(file_path)

            # Validate file exists
            if not path.exists():
                raise ToolExecutionError(self.name, f"File not found: {file_path}")

            # Validate it's a file
            if not path.is_file():
                raise ToolExecutionError(self.name, f"Path is not a file: {file_path}")

            # Validate it's a Java file
            if path.suffix.lower() != ".java":
                raise ToolExecutionError(
                    self.name,
                    f"Not a Java file (expected .java extension): {file_path}",
                )

            # Read the file
            content = path.read_text(encoding="utf-8")

            # Calculate statistics
            lines = content.split("\n")
            total_lines = len(lines)
            non_empty_lines = len([line for line in lines if line.strip()])
            comment_lines = len(
                [
                    line
                    for line in lines
                    if line.strip().startswith("//") or line.strip().startswith("*")
                ]
            )

            # Format output for the agent
            result = []
            result.append(f"📄 File: {path.name}")
            result.append(f"📍 Path: {file_path}")
            result.append("📊 Statistics:")
            result.append(f"   - Total lines: {total_lines}")
            result.append(f"   - Non-empty lines: {non_empty_lines}")
            result.append(f"   - Comment lines: {comment_lines}")
            result.append(f"   - Code lines (approx): {non_empty_lines - comment_lines}")
            result.append("")
            result.append("📝 Contents:")
            result.append("=" * 70)

            # Add line numbers to content
            for i, line in enumerate(lines, 1):
                result.append(f"{i:4d} | {line}")

            result.append("=" * 70)

            return "\n".join(result)

        except ToolExecutionError:
            raise
        except Exception as e:
            raise ToolExecutionError(self.name, f"Failed to read file: {str(e)}")
