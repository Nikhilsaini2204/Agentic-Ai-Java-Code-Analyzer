#!/usr/bin/env python3
"""
Health check script - verifies system setup and readiness.
Can be run standalone or via 'make health'.
"""

import sys
from pathlib import Path

# Add both src and project root to path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

from analyzer.utils.health import run_health_check


def main():
    """Run health check."""
    print("=" * 70)
    print("Java Code Analyzer - System Health Check")
    print("=" * 70)

    success = run_health_check(verbose=True)

    print("\n" + "=" * 70)

    if success:
        print("✅ System is ready! You can start building the agent.")
        print("\nNext steps:")
        print("  1. Verify: make test")
        print("  2. Start coding: Open src/analyzer/core/agent.py")
        return 0
    else:
        print("❌ System has issues. Please fix them before proceeding.")
        print("\nCommon fixes:")
        print("  - Set GROQ_API_KEY in .env file")
        print("  - Run: pip install -r requirements-dev.txt")
        print("  - Check file permissions in data/ directory")
        return 1


if __name__ == "__main__":
    sys.exit(main())