"""
Tests for health check system.
"""

import pytest

from analyzer.utils.health import HealthCheck, quick_check


class TestHealthCheck:
    """Test health check functionality."""

    def test_health_check_instance(self):
        """Test creating health check instance."""
        checker = HealthCheck()
        assert checker is not None
        assert len(checker.checks) == 0

    def test_add_check(self):
        """Test adding check results."""
        checker = HealthCheck()
        checker.add_check("Test Check", True, "Test passed")

        assert len(checker.checks) == 1
        name, passed, message = checker.checks[0]
        assert name == "Test Check"
        assert passed is True
        assert message == "Test passed"

    def test_check_python_version(self):
        """Test Python version check."""
        checker = HealthCheck()
        result = checker.check_python_version()

        # Should pass since we're running on Python 3.11+
        assert result is True
        assert len(checker.checks) == 1

    def test_check_dependencies(self):
        """Test dependency check."""
        checker = HealthCheck()
        result = checker.check_dependencies()

        # Should pass if all dependencies are installed
        assert result is True
        assert len(checker.checks) > 0

    def test_check_settings_load(self):
        """Test settings loading check."""
        checker = HealthCheck()
        result = checker.check_settings_load()

        # Should pass if settings load correctly
        assert result is True

    def test_check_directories(self):
        """Test directory existence check."""
        checker = HealthCheck()
        result = checker.check_directories()

        # Should pass since directories are created by settings
        assert result is True

    def test_get_system_info(self):
        """Test getting system information."""
        checker = HealthCheck()
        info = checker.get_system_info()

        assert "Python Version" in info
        assert "Platform" in info
        assert "Environment" in info
        assert "Primary LLM" in info

    def test_quick_check(self):
        """Test quick check function."""
        result = quick_check()

        # Should return a boolean
        assert isinstance(result, bool)


@pytest.mark.integration
class TestHealthCheckIntegration:
    """Integration tests for health check."""

    def test_full_health_check(self):
        """Test running full health check."""
        checker = HealthCheck()
        result = checker.run_all_checks()

        # Should complete without errors
        assert isinstance(result, bool)
        assert len(checker.checks) > 0

    def test_print_results(self):
        """Test printing results doesn't crash."""
        checker = HealthCheck()
        checker.run_all_checks()

        # Should not raise exception
        try:
            checker.print_results()
            assert True
        except Exception as e:
            pytest.fail(f"print_results raised exception: {e}")

    def test_print_system_info(self):
        """Test printing system info doesn't crash."""
        checker = HealthCheck()

        # Should not raise exception
        try:
            checker.print_system_info()
            assert True
        except Exception as e:
            pytest.fail(f"print_system_info raised exception: {e}")
