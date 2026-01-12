"""
Tool for calculating code complexity metrics.
"""

import re
from pathlib import Path

from analyzer.tools.base import BaseTool, ToolParameter
from analyzer.utils.exceptions import ToolExecutionError


class ComplexityAnalysisTool(BaseTool):
    """
    Calculates code complexity metrics including:
    - Cyclomatic complexity
    - Nesting depth
    - Method count
    - Lines of code
    """

    @property
    def name(self) -> str:
        return "complexity_analysis"

    @property
    def description(self) -> str:
        return (
            "Calculates code complexity metrics: cyclomatic complexity, "
            "nesting depth, method count, lines of code. "
            "Use this to identify overly complex code that may need refactoring."
        )

    def get_parameters(self) -> dict[str, ToolParameter]:
        return {
            "file_path": ToolParameter(
                name="file_path",
                type="string",
                description="Path to the Java file to analyze",
                required=True,
            )
        }

    def execute(self, file_path: str, **kwargs) -> str:
        """Calculate complexity metrics for a Java file."""
        try:
            path = Path(file_path)

            if not path.exists():
                raise ToolExecutionError(self.name, f"File not found: {file_path}")

            code = path.read_text(encoding="utf-8")
            lines = code.split("\n")

            # Calculate metrics
            metrics = {
                "total_lines": len(lines),
                "code_lines": self._count_code_lines(lines),
                "comment_lines": self._count_comment_lines(lines),
                "blank_lines": self._count_blank_lines(lines),
                "method_count": self._count_methods(code),
                "class_count": self._count_classes(code),
                "cyclomatic_complexity": self._calculate_cyclomatic_complexity(code),
                "max_nesting_depth": self._calculate_max_nesting(code),
            }

            # Calculate derived metrics
            if metrics["method_count"] > 0:
                metrics["avg_method_length"] = metrics["code_lines"] // metrics["method_count"]
            else:
                metrics["avg_method_length"] = 0

            return self._format_report(path.name, metrics)

        except ToolExecutionError:
            raise
        except Exception as e:
            raise ToolExecutionError(self.name, f"Complexity analysis failed: {str(e)}")

    def _count_code_lines(self, lines: list) -> int:
        """Count non-empty, non-comment lines."""
        code_lines = 0
        in_block_comment = False

        for line in lines:
            stripped = line.strip()

            # Handle block comments
            if "/*" in stripped:
                in_block_comment = True
            if "*/" in stripped:
                in_block_comment = False
                continue

            if in_block_comment:
                continue

            # Skip empty lines and single-line comments
            if stripped and not stripped.startswith("//") and not stripped.startswith("*"):
                code_lines += 1

        return code_lines

    def _count_comment_lines(self, lines: list) -> int:
        """Count comment lines."""
        comment_lines = 0
        in_block_comment = False

        for line in lines:
            stripped = line.strip()

            if "/*" in stripped:
                in_block_comment = True
                comment_lines += 1
                continue

            if in_block_comment:
                comment_lines += 1
                if "*/" in stripped:
                    in_block_comment = False
                continue

            if stripped.startswith("//") or stripped.startswith("*"):
                comment_lines += 1

        return comment_lines

    def _count_blank_lines(self, lines: list) -> int:
        """Count blank lines."""
        return sum(1 for line in lines if not line.strip())

    def _count_methods(self, code: str) -> int:
        """Count method definitions."""
        # Match method signatures
        pattern = (
            r"(public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\([^\)]*\)\s*(\{|throws)"
        )
        return len(re.findall(pattern, code))

    def _count_classes(self, code: str) -> int:
        """Count class definitions."""
        pattern = r"\b(class|interface|enum)\s+\w+"
        return len(re.findall(pattern, code))

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """
        Calculate cyclomatic complexity.

        Formula: M = E - N + 2P
        Simplified: Count decision points + 1
        """
        # Count decision points
        if_count = len(re.findall(r"\bif\s*\(", code))
        for_count = len(re.findall(r"\bfor\s*\(", code))
        while_count = len(re.findall(r"\bwhile\s*\(", code))
        case_count = len(re.findall(r"\bcase\s+", code))
        catch_count = len(re.findall(r"\bcatch\s*\(", code))
        ternary_count = len(re.findall(r"\?[^:]+:", code))
        and_or_count = len(re.findall(r"(\&\&|\|\|)", code))

        # Cyclomatic complexity = decision points + 1
        complexity = (
            1
            + if_count
            + for_count
            + while_count
            + case_count
            + catch_count
            + ternary_count
            + and_or_count
        )

        return complexity

    def _calculate_max_nesting(self, code: str) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0
        current_depth = 0

        for char in code:
            if char == "{":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == "}":
                current_depth = max(0, current_depth - 1)

        return max_depth

    def _format_report(self, filename: str, metrics: dict) -> str:
        """Format complexity report."""
        result = []
        result.append(f"📊 Complexity Analysis Report: {filename}")
        result.append("=" * 70)

        # Basic metrics
        result.append("\n📏 Size Metrics:")
        result.append(f"   Total Lines:        {metrics['total_lines']:5d}")
        result.append(f"   Code Lines:         {metrics['code_lines']:5d}")
        result.append(f"   Comment Lines:      {metrics['comment_lines']:5d}")
        result.append(f"   Blank Lines:        {metrics['blank_lines']:5d}")

        # Structure metrics
        result.append("\n🏗️  Structure:")
        result.append(f"   Classes:            {metrics['class_count']:5d}")
        result.append(f"   Methods:            {metrics['method_count']:5d}")
        result.append(f"   Avg Method Length:  {metrics['avg_method_length']:5d} lines")

        # Complexity metrics
        result.append("\n🔀 Complexity:")
        cc = metrics["cyclomatic_complexity"]

        if cc <= 10:
            cc_status = "✅ Low (Good)"
        elif cc <= 20:
            cc_status = "⚠️  Moderate (Consider refactoring)"
        elif cc <= 50:
            cc_status = "🔴 High (Refactoring recommended)"
        else:
            cc_status = "🚨 Very High (Critical - refactor immediately)"

        result.append(f"   Cyclomatic Complexity: {cc:3d}  {cc_status}")

        depth = metrics["max_nesting_depth"]

        if depth <= 3:
            depth_status = "✅ Good"
        elif depth <= 5:
            depth_status = "⚠️  Moderate (simplify if possible)"
        else:
            depth_status = "🔴 Too deep (refactor to reduce nesting)"

        result.append(f"   Max Nesting Depth:     {depth:3d}  {depth_status}")

        result.append("")

        # Overall assessment
        result.append("\n📋 Assessment:")

        issues = []
        if cc > 20:
            issues.append("High cyclomatic complexity")
        if depth > 5:
            issues.append("Deep nesting")
        if metrics["avg_method_length"] > 50:
            issues.append("Long methods")

        if not issues:
            result.append("   ✅ Code complexity is within acceptable limits")
        else:
            result.append("   ⚠️  Issues detected:")
            for issue in issues:
                result.append(f"      - {issue}")

        # Recommendations
        if issues:
            result.append("\n💡 Recommendations:")
            if cc > 20:
                result.append("   - Break down complex methods into smaller functions")
                result.append("   - Consider using design patterns to simplify logic")
            if depth > 5:
                result.append("   - Extract nested code into separate methods")
                result.append("   - Use early returns to reduce nesting")
            if metrics["avg_method_length"] > 50:
                result.append("   - Split long methods into focused, single-purpose methods")

        result.append("\n" + "=" * 70)

        return "\n".join(result)
