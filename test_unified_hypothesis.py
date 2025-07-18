"""
Tests for UnifiedHypothesis class.
"""

import pytest
from datetime import datetime
from jnana.data.unified_hypothesis import UnifiedHypothesis, FeedbackEntry, Reference
from jnana.data.data_migration import DataMigration
from jnana.protognosis.core.agent_core import ResearchHypothesis


def test_unified_hypothesis_creation():
    """Test basic hypothesis creation."""
    hypothesis = UnifiedHypothesis(
        title="Test Hypothesis",
        description="This is a test hypothesis for validation."
    )
    
    assert hypothesis.title == "Test Hypothesis"
    assert hypothesis.description == "This is a test hypothesis for validation."
    assert hypothesis.content == "This is a test hypothesis for validation."  # Should sync
    assert hypothesis.version == 1
    assert hypothesis.version_string == "1.0"
    assert hypothesis.hypothesis_type == "original"


def test_feedback_addition():
    """Test adding feedback to hypothesis."""
    hypothesis = UnifiedHypothesis(
        title="Test Hypothesis",
        description="Initial description"
    )
    
    initial_version = hypothesis.version_string
    hypothesis.add_feedback("Please make it more specific")
    
    assert len(hypothesis.feedback_history) == 1
    assert hypothesis.feedback_history[0].feedback == "Please make it more specific"
    assert hypothesis.version_string != initial_version
    assert hypothesis.version == 2
    assert hypothesis.version_string == "1.1"


def test_version_increment():
    """Test version incrementing."""
    hypothesis = UnifiedHypothesis(title="Test")
    
    assert hypothesis.version_string == "1.0"
    
    hypothesis.increment_version()
    assert hypothesis.version_string == "1.1"
    
    hypothesis.increment_version()
    assert hypothesis.version_string == "1.2"


def test_reference_addition():
    """Test adding references."""
    hypothesis = UnifiedHypothesis(title="Test")
    
    hypothesis.add_reference(
        citation="Smith, J. (2024). Test Research. Journal of Testing, 1(1), 1-10.",
        annotation="This paper provides foundational concepts."
    )
    
    assert len(hypothesis.references) == 1
    assert hypothesis.references[0].citation.startswith("Smith, J.")
    assert hypothesis.references[0].annotation == "This paper provides foundational concepts."


def test_tournament_record():
    """Test tournament record functionality."""
    hypothesis = UnifiedHypothesis(title="Test")
    
    # Initial state
    assert hypothesis.get_win_rate() == 0.0
    
    # Add wins and losses
    hypothesis.update_tournament_record(True, "opponent1")
    hypothesis.update_tournament_record(False, "opponent2")
    hypothesis.update_tournament_record(True, "opponent3")
    
    assert hypothesis.tournament_record.wins == 2
    assert hypothesis.tournament_record.losses == 1
    assert hypothesis.get_win_rate() == 2/3


def test_wisteria_format_conversion():
    """Test conversion to Wisteria format."""
    hypothesis = UnifiedHypothesis(
        title="Test Hypothesis",
        description="Test description",
        experimental_validation="Test validation plan"
    )
    
    hypothesis.add_feedback("Test feedback")
    hypothesis.add_reference("Test citation", "Test annotation")
    
    wisteria_format = hypothesis.to_wisteria_format()
    
    assert wisteria_format["title"] == "Test Hypothesis"
    assert wisteria_format["description"] == "Test description"
    assert wisteria_format["experimental_validation"] == "Test validation plan"
    assert len(wisteria_format["feedback_history"]) == 1
    assert len(wisteria_format["references"]) == 1


def test_protognosis_format_conversion():
    """Test conversion to ProtoGnosis format."""
    hypothesis = UnifiedHypothesis(
        title="Test Hypothesis",
        content="Test content"
    )
    
    hypothesis.update_tournament_record(True, "opponent1")
    
    protognosis_format = hypothesis.to_protognosis_format()
    
    assert protognosis_format["content"] == "Test content"
    assert protognosis_format["metadata"]["title"] == "Test Hypothesis"
    assert protognosis_format["tournament_record"]["wins"] == 1


def test_protognosis_to_unified():
    """Test conversion to Unified format from protognosis"""
    protognosis_format = ResearchHypothesis(
            content = "Test content",
            summary = "example summary",
            agent_id = "generation-test",
            hypothesis_id = "id-id-id-id",
            elo_rating = 1200.0,
            metadata = {
                "title":"Test Hypothesis"
                }
            )
    protognosis_dict = protognosis_format.to_dict()

    unified_format = DataMigration.from_protognosis(protognosis_dict)
    assert unified_format.title == "Test Hypothesis"


def test_agent_contribution():
    """Test agent contribution tracking."""
    hypothesis = UnifiedHypothesis(title="Test")
    
    hypothesis.add_agent_contribution(
        agent_id="gen_001",
        agent_type="generation",
        contribution_type="initial_generation",
        details={"strategy": "literature_exploration"}
    )
    
    assert len(hypothesis.agent_contributions) == 1
    contribution = hypothesis.agent_contributions[0]
    assert contribution.agent_id == "gen_001"
    assert contribution.agent_type == "generation"
    assert contribution.contribution_type == "initial_generation"
    assert contribution.details["strategy"] == "literature_exploration"


def test_hypothesis_serialization():
    """Test hypothesis serialization and deserialization."""
    original = UnifiedHypothesis(
        title="Serialization Test",
        description="Testing serialization functionality"
    )
    
    original.add_feedback("Test feedback")
    original.add_reference("Test citation")
    
    # Convert to dict and back
    data = original.to_dict()
    restored = UnifiedHypothesis.from_dict(data)
    
    assert restored.title == original.title
    assert restored.description == original.description
    assert len(restored.feedback_history) == len(original.feedback_history)
    assert len(restored.references) == len(original.references)


if __name__ == "__main__":
    pytest.main([__file__])
