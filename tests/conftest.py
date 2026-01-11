"""
Pytest configuration and fixtures.
"""

import sys
from pathlib import Path

import pytest

# Add both src and project root to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_java_code() -> str:
    """Sample Java code for testing."""
    return """
public class SampleCode {
    public void processData(String input) {
        System.out.println("Processing: " + input);
    }
    
    public int calculate(int a, int b) {
        return a + b;
    }
}
"""


@pytest.fixture
def bad_java_code() -> str:
    """Bad Java code with issues for testing."""
    return """
public class BadCode {
    public void unsafeMethod(String userInput) {
        // SQL injection vulnerability
        String query = "SELECT * FROM users WHERE id = '" + userInput + "'";
        
        try {
            // Some risky operation
        } catch (Exception e) {
            // Empty catch block
        }
    }
}
"""


@pytest.fixture
def temp_java_file(tmp_path, sample_java_code):
    """Create a temporary Java file."""
    java_file = tmp_path / "Test.java"
    java_file.write_text(sample_java_code)
    return java_file
