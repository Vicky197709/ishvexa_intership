import pytest
from apps.events.services import generate_fingerprint


class TestGenerateFingerprint:
    """Tests for the fingerprint generation logic."""
    
    def test_fingerprint_with_message_only(self):
        """Test fingerprint generation with only message."""
        message = "Error occurred"
        fingerprint = generate_fingerprint(message)
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hex length
    
    def test_fingerprint_with_stack_trace(self):
        """Test fingerprint generation with message and stack trace."""
        message = "Error occurred"
        stack_trace = "File 'app.py', line 10\n  main()"
        fingerprint = generate_fingerprint(message, stack_trace)
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64
    
    def test_fingerprint_normalizes_message(self):
        """Test that message is normalized (trimmed and lowercased)."""
        message1 = "  ERROR OCCURRED  "
        message2 = "error occurred"
        
        fp1 = generate_fingerprint(message1)
        fp2 = generate_fingerprint(message2)
        
        assert fp1 == fp2
    
    def test_fingerprint_uses_top_stack_frame(self):
        """Test that fingerprint uses only the top stack frame."""
        message = "Error occurred"
        stack_trace1 = "Frame 1\nFrame 2\nFrame 3"
        stack_trace2 = "Frame 1\nDifferent frame"
        
        fp1 = generate_fingerprint(message, stack_trace1)
        fp2 = generate_fingerprint(message, stack_trace2)
        
        assert fp1 == fp2
    
    def test_fingerprint_different_top_frames(self):
        """Test that different top frames produce different fingerprints."""
        message = "Error occurred"
        stack_trace1 = "Frame 1"
        stack_trace2 = "Frame 2"
        
        fp1 = generate_fingerprint(message, stack_trace1)
        fp2 = generate_fingerprint(message, stack_trace2)
        
        assert fp1 != fp2
    
    def test_fingerprint_consistent(self):
        """Test that same inputs produce same fingerprint."""
        message = "Error occurred"
        stack_trace = "Frame 1"
        
        fp1 = generate_fingerprint(message, stack_trace)
        fp2 = generate_fingerprint(message, stack_trace)
        
        assert fp1 == fp2
