"""
Tool for performing static analysis on Java code.
"""

import re
from pathlib import Path

from analyzer.tools.base import BaseTool, ToolParameter
from analyzer.utils.exceptions import ToolExecutionError


class StaticAnalysisTool(BaseTool):
    """
    Performs static analysis to find code quality issues.

    Detects:
    - Code smells
    - Bad practices
    - Potential bugs
    - Security issues
    """

    @property
    def name(self) -> str:
        return "static_analysis"

    @property
    def description(self) -> str:
        return (
            "Performs static code analysis to detect issues like: "
            "System.out.println usage, empty catch blocks, printStackTrace calls, "
            "SQL injection risks, hardcoded credentials, TODO comments, and other code smells. "
            "Returns a detailed report of all issues found."
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
        """Perform static analysis on a Java file."""
        try:
            path = Path(file_path)

            if not path.exists():
                raise ToolExecutionError(self.name, f"File not found: {file_path}")

            code = path.read_text(encoding="utf-8")
            lines = code.split("\n")

            issues = []

            # Check 1: System.out.println usage
            issues.extend(self._check_system_out(lines))

            # Check 2: Empty catch blocks
            issues.extend(self._check_empty_catch(code, lines))

            # Check 3: printStackTrace usage
            issues.extend(self._check_printstacktrace(lines))

            # Check 4: SQL injection risks
            issues.extend(self._check_sql_injection(lines))

            # Check 5: Hardcoded credentials
            issues.extend(self._check_hardcoded_credentials(lines))

            # Check 6: TODO comments
            issues.extend(self._check_todos(lines))

            # Check 7: Magic numbers
            issues.extend(self._check_magic_numbers(lines))

            # Check 8: Long methods
            issues.extend(self._check_long_methods(code))

            # Format output
            return self._format_report(path.name, issues)

        except ToolExecutionError:
            raise
        except Exception as e:
            raise ToolExecutionError(self.name, f"Analysis failed: {str(e)}")

    def _check_system_out(self, lines: list[str]) -> list[tuple[str, int, str]]:
        """Check for System.out usage."""
        issues = []
        for i, line in enumerate(lines, 1):
            if "System.out.println" in line or "System.out.print" in line:
                issues.append(
                    (
                        "STYLE",
                        i,
                        "Using System.out instead of proper logging framework",
                    )
                )
        return issues

    def _check_empty_catch(self, code: str, lines: list[str]) -> list[tuple[str, int, str]]:
        """Check for empty catch blocks."""
        issues = []
        # Simple pattern: catch followed by empty braces
        pattern = r"catch\s*\([^)]+\)\s*\{\s*\}"
        for match in re.finditer(pattern, code):
            line_num = code[: match.start()].count("\n") + 1
            issues.append(("BUG", line_num, "Empty catch block - exceptions should be handled"))
        return issues

    def _check_printstacktrace(self, lines: list[str]) -> list[tuple[str, int, str]]:
        """Check for printStackTrace usage."""
        issues = []
        for i, line in enumerate(lines, 1):
            if "printStackTrace()" in line:
                issues.append(
                    (
                        "STYLE",
                        i,
                        "Using printStackTrace() - use proper logging instead",
                    )
                )
        return issues

    def _check_sql_injection(self, lines: list[str]) -> list[tuple[str, int, str]]:
        """Check for potential SQL injection vulnerabilities."""
        issues = []
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP"]

        for i, line in enumerate(lines, 1):
            # Check for string concatenation with SQL keywords
            for keyword in sql_keywords:
                if f'"{keyword}' in line and "+" in line:
                    issues.append(
                        (
                            "SECURITY",
                            i,
                            f"Potential SQL injection - {keyword} statement with string concatenation",
                        )
                    )
                    break
        return issues

    def _check_hardcoded_credentials(self, lines: list[str]) -> list[tuple[str, int, str]]:
        """Check for hardcoded passwords or API keys."""
        issues = []
        patterns = [
            (r'password\s*=\s*"[^"]+', "Possible hardcoded password"),
            (r'api_key\s*=\s*"[^"]+', "Possible hardcoded API key"),
            (r'secret\s*=\s*"[^"]+', "Possible hardcoded secret"),
        ]

        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            for pattern, message in patterns:
                if re.search(pattern, line_lower):
                    issues.append(("SECURITY", i, message))
                    break
        return issues

    def _check_todos(self, lines: list[str]) -> list[tuple[str, int, str]]:
        """Check for TODO comments."""
        issues = []
        for i, line in enumerate(lines, 1):
            if "TODO" in line or "FIXME" in line:
                issues.append(("MAINTENANCE", i, "TODO/FIXME comment - incomplete code"))
        return issues

    def _check_magic_numbers(self, lines: list[str]) -> list[tuple[str, int, str]]:
        """Check for magic numbers."""
        issues = []
        # Look for numeric literals (excluding 0, 1, -1 which are often okay)
        pattern = r"\b\d{2,}\b"

        for i, line in enumerate(lines, 1):
            # Skip comments and strings
            if line.strip().startswith("//") or line.strip().startswith("*"):
                continue

            matches = re.findall(pattern, line)
            if matches and not any(x in line for x in ["private", "public", "final"]):
                issues.append(
                    (
                        "STYLE",
                        i,
                        f"Magic number(s) detected: {', '.join(matches)} - consider using named constants",
                    )
                )
        return issues

    def _check_long_methods(self, code: str) -> list[tuple[str, int, str]]:
        """Check for methods that are too long."""
        issues = []
        # Simple heuristic: method followed by lots of lines before closing brace
        method_pattern = r"(public|private|protected)\s+\w+\s+\w+\s*\([^)]*\)\s*\{"

        for match in re.finditer(method_pattern, code):
            start_line = code[: match.start()].count("\n") + 1
            # Count lines until matching closing brace (simplified)
            remaining = code[match.end() :]
            brace_count = 1
            lines_in_method = 0

            for char in remaining:
                if char == "\n":
                    lines_in_method += 1
                elif char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        break

            if lines_in_method > 50:
                issues.append(
                    (
                        "COMPLEXITY",
                        start_line,
                        f"Method is too long ({lines_in_method} lines) - consider refactoring",
                    )
                )

        return issues

    def _format_report(self, filename: str, issues: list[tuple[str, int, str]]) -> str:
        """Format the analysis report."""
        result = []
        result.append(f"🔍 Static Analysis Report: {filename}")
        result.append("=" * 70)

        if not issues:
            result.append("✅ No issues found! Code looks clean.")
            return "\n".join(result)

        # Group by severity
        by_severity = {
            "SECURITY": [],
            "BUG": [],
            "COMPLEXITY": [],
            "STYLE": [],
            "MAINTENANCE": [],
        }

        for severity, line, message in issues:
            by_severity[severity].append((line, message))

        # Print by severity (most important first)
        severity_order = ["SECURITY", "BUG", "COMPLEXITY", "STYLE", "MAINTENANCE"]
        severity_icons = {
            "SECURITY": "🚨",
            "BUG": "🐛",
            "COMPLEXITY": "📊",
            "STYLE": "💅",
            "MAINTENANCE": "🔧",
        }

        total_issues = 0
        for severity in severity_order:
            issues_list = by_severity[severity]
            if issues_list:
                result.append(f"\n{severity_icons[severity]} {severity} Issues:")
                for line, message in sorted(issues_list):
                    result.append(f"   Line {line:4d}: {message}")
                    total_issues += 1

        result.append("\n" + "=" * 70)
        result.append(f"Total issues found: {total_issues}")

        # Provide priority recommendation
        if by_severity["SECURITY"]:
            result.append("\n⚠️  PRIORITY: Address security issues immediately!")
        elif by_severity["BUG"]:
            result.append("\n⚠️  PRIORITY: Fix potential bugs before deploying!")

        return "\n".join(result)
