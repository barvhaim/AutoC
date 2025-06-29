"""Unit tests for backend core functionality."""

import pytest
from unittest.mock import Mock, patch
from backend.run import run
from backend.data_model.ioc import IOC, IOCType


class TestBackendRun:
    """Test cases for the core run function."""

    @patch('backend.run.build_graph')
    @patch('backend.run.get_positive_qna')
    def test_run_ping_mode(self, mock_get_positive_qna, mock_build_graph):
        """Test run function in ping mode."""
        # Setup mocks
        mock_graph = Mock()
        mock_build_graph.return_value = mock_graph
        
        mock_result = {
            "keywords_found": ["malware", "threat"],
            "qna": [
                {"question": "What threats are mentioned?", "answer": "Malware XYZ"},
                {"question": "Are there IoCs?", "answer": "Yes, several IPs"}
            ],
            "error": None
        }
        mock_graph.invoke.return_value = mock_result
        
        mock_get_positive_qna.return_value = [
            {"question": "Are there IoCs?", "answer": "Yes, several IPs"}
        ]
        
        # Execute
        result = run(
            url="https://example.com/blog", 
            ping=True,
            keywords=["test"],
            analyst_questions=["Any threats?"]
        )
        
        # Verify
        assert result == {
            "keywords_found": ["malware", "threat"],
            "positive_analyst_questions": [
                {"question": "Are there IoCs?", "answer": "Yes, several IPs"}
            ]
        }
        
        mock_build_graph.assert_called_once()
        mock_graph.invoke.assert_called_once()
        mock_get_positive_qna.assert_called_once_with(qna=mock_result["qna"])

    @patch('backend.run.build_graph')
    def test_run_full_analysis_mode(self, mock_build_graph):
        """Test run function in full analysis mode."""
        # Setup mocks
        mock_graph = Mock()
        mock_build_graph.return_value = mock_graph
        
        # Create mock IoC objects
        mock_ioc1 = Mock()
        mock_ioc1.model_dump.return_value = {
            "type": IOCType.IP,
            "value": "192.168.1.1"
        }
        
        mock_ioc2 = Mock()
        mock_ioc2.model_dump.return_value = {
            "type": IOCType.URL,
            "value": "https://malicious.com"
        }
        
        mock_result = {
            "article_textual_content": "Blog post content about threats...",
            "keywords_found": ["malware", "botnet"],
            "qna": [{"question": "What is the main threat?", "answer": "Botnet activity"}],
            "iocs_found": [mock_ioc1, mock_ioc2],
            "mitre_ttps": [
                {"id": "T1055", "name": "Process Injection", "confidence": 0.85}
            ],
            "error": None
        }
        mock_graph.invoke.return_value = mock_result
        
        # Execute
        result = run(url="https://example.com/threat-report")
        
        # Verify
        expected_result = {
            "article_textual_content": "Blog post content about threats...",
            "keywords_found": ["malware", "botnet"],
            "qna": [{"question": "What is the main threat?", "answer": "Botnet activity"}],
            "iocs_found": [
                {"type": "IP Address", "value": "192.168.1.1"},
                {"type": "Domain or URL", "value": "https://malicious.com"}
            ],
            "mitre_ttps": [
                {"id": "T1055", "name": "Process Injection", "confidence": 0.85}
            ]
        }
        
        assert result == expected_result
        mock_build_graph.assert_called_once()
        mock_graph.invoke.assert_called_once()

    @patch('backend.run.build_graph')
    def test_run_with_raw_text(self, mock_build_graph):
        """Test run function with raw text input."""
        # Setup mocks
        mock_graph = Mock()
        mock_build_graph.return_value = mock_graph
        
        mock_result = {
            "article_textual_content": "Raw text analysis...",
            "keywords_found": ["phishing"],
            "qna": [],
            "iocs_found": [],
            "mitre_ttps": None,
            "error": None
        }
        mock_graph.invoke.return_value = mock_result
        
        # Execute
        result = run(raw_text="Some raw text content to analyze")
        
        # Verify
        expected_inputs = {
            "url": None,
            "settings": {
                "skip_ioc_extraction": False,
                "keywords": [],
                "analyst_questions": []
            },
            "article_textual_content": "Some raw text content to analyze",
            "qna": [],
            "keywords_found": [],
            "iocs_found": [],
            "mitre_ttps": None,
            "error": None
        }
        
        mock_graph.invoke.assert_called_once_with(input=expected_inputs)
        assert result["article_textual_content"] == "Raw text analysis..."

    @patch('backend.run.build_graph')
    def test_run_with_error(self, mock_build_graph):
        """Test run function when graph returns an error."""
        # Setup mocks
        mock_graph = Mock()
        mock_build_graph.return_value = mock_graph
        
        mock_result = {
            "error": "Failed to fetch URL content"
        }
        mock_graph.invoke.return_value = mock_result
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Failed to fetch URL content"):
            run(url="https://invalid-url.com")

    @patch('backend.run.build_graph')
    def test_run_input_parameters(self, mock_build_graph):
        """Test that run function properly formats input parameters."""
        # Setup mocks
        mock_graph = Mock()
        mock_build_graph.return_value = mock_graph
        
        mock_result = {
            "article_textual_content": "content",
            "keywords_found": [],
            "qna": [],
            "iocs_found": [],
            "mitre_ttps": None,
            "error": None
        }
        mock_graph.invoke.return_value = mock_result
        
        # Execute
        run(
            url="https://test.com",
            keywords=["test", "keywords"],
            analyst_questions=["Question 1", "Question 2"]
        )
        
        # Verify the input structure passed to graph
        call_args = mock_graph.invoke.call_args
        inputs = call_args[1]["input"]  # keyword argument 'input'
        
        assert inputs["url"] == "https://test.com"
        assert inputs["settings"]["keywords"] == ["test", "keywords"]
        assert inputs["settings"]["analyst_questions"] == ["Question 1", "Question 2"]
        assert inputs["settings"]["skip_ioc_extraction"] is False