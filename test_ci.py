"""
CI-friendly tests that don't require Elasticsearch connection.
Tests basic project structure and configuration files.
"""
import pytest
from pathlib import Path


def test_project_structure():
    """Test that all required files exist."""
    project_root = Path(__file__).parent
    assert (project_root / "src" / "agent" / "triage_agent.py").exists()
    assert (project_root / "src" / "es_config" / "es_manager.py").exists()
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


def test_source_code_exists():
    """Test that main source files exist and are non-empty."""
    project_root = Path(__file__).parent
    
    # Check triage agent
    triage_agent_path = project_root / "src" / "agent" / "triage_agent.py"
    assert triage_agent_path.exists()
    assert triage_agent_path.stat().st_size > 1000  # Should be substantial
    
    # Check data generator
    data_gen_path = project_root / "src" / "data_generator.py"
    assert data_gen_path.exists()
    
    # Check ES config
    es_config_path = project_root / "src" / "es_config" / "es_manager.py"
    assert es_config_path.exists()


def test_documentation_exists():
    """Test that documentation files exist."""
    project_root = Path(__file__).parent
    assert (project_root / "README.md").exists()
    assert (project_root / "DEMO_SCRIPT.md").exists()
    assert (project_root / "SUBMISSION_DESCRIPTION.md").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
