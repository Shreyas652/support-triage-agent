"""
CI-friendly tests that don't require Elasticsearch connection.
Tests basic imports and configuration validation.
"""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all main modules can be imported."""
    from agent.triage_agent import TriageAgent
    from config.elasticsearch_config import get_elasticsearch_config
    assert TriageAgent is not None
    assert get_elasticsearch_config is not None


def test_project_structure():
    """Test that all required files exist."""
    project_root = Path(__file__).parent
    assert (project_root / "src" / "agent" / "triage_agent.py").exists()
    assert (project_root / "src" / "config" / "elasticsearch_config.py").exists()
    assert (project_root / "requirements.txt").exists()
    assert (project_root / "environment.yml").exists()
    assert (project_root / "README.md").exists()


def test_requirements_file():
    """Test that requirements.txt is valid."""
    requirements_path = Path(__file__).parent / "requirements.txt"
    with open(requirements_path, 'r') as f:
        content = f.read()
    assert "elasticsearch" in content
    assert "python-dotenv" in content
    assert "pytest" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
