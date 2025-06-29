"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from api.server import app, extract_inputs
from api.data_models import AnalyzeRequest, FeedbackRequest


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestExtractInputs:
    """Test cases for the extract_inputs function."""

    def test_extract_inputs_with_url(self):
        """Test extract_inputs with URL."""
        request = AnalyzeRequest(
            url="https://example.com/blog",
            keywords=["malware", "threat"],
            analyst_questions=["What IoCs are present?"]
        )
        
        url, raw_text, keywords, analyst_questions = extract_inputs(request)
        
        assert url == "https://example.com/blog"
        assert raw_text is None
        assert keywords == ["malware", "threat"]
        assert analyst_questions == ["What IoCs are present?"]

    def test_extract_inputs_with_raw_text(self):
        """Test extract_inputs with raw text."""
        request = AnalyzeRequest(
            raw_text="Some blog content to analyze...",
            keywords=["phishing"],
            analyst_questions=[]
        )
        
        url, raw_text, keywords, analyst_questions = extract_inputs(request)
        
        assert url is None
        assert raw_text == "Some blog content to analyze..."
        assert keywords == ["phishing"]
        assert analyst_questions == []

    def test_extract_inputs_minimal(self):
        """Test extract_inputs with minimal data."""
        request = AnalyzeRequest()
        
        url, raw_text, keywords, analyst_questions = extract_inputs(request)
        
        assert url is None
        assert raw_text is None
        assert keywords == []
        assert analyst_questions == []

    def test_extract_inputs_both_url_and_text_error(self):
        """Test extract_inputs raises error when both URL and text provided."""
        from fastapi import HTTPException
        
        request = AnalyzeRequest(
            url="https://example.com",
            raw_text="Some text content"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            extract_inputs(request)
        
        assert exc_info.value.status_code == 400
        assert "Both 'url' and 'raw_text' cannot be provided simultaneously" in str(exc_info.value.detail)


class TestHealthEndpoint:
    """Test cases for the health check endpoint."""

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestPingEndpoint:
    """Test cases for the ping endpoint."""

    @patch('api.server.run')
    def test_ping_endpoint_success(self, mock_run, client):
        """Test successful ping endpoint call."""
        # Setup mock
        mock_run.return_value = {
            "keywords_found": ["malware", "botnet"],
            "positive_analyst_questions": [
                {"question": "Are there IoCs?", "answer": "Yes, several IPs"}
            ]
        }
        
        # Make request
        request_data = {
            "url": "https://example.com/blog",
            "keywords": ["test"],
            "analyst_questions": ["Any threats mentioned?"]
        }
        
        response = client.post("/api/v1/ping", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["url"] == "https://example.com/blog"
        assert response_data["keywords_found"] == ["malware", "botnet"]
        assert len(response_data["positive_analyst_questions"]) == 1
        
        # Verify mock was called correctly
        mock_run.assert_called_once_with(
            url="https://example.com/blog",
            ping=True,
            keywords=["test"],
            analyst_questions=["Any threats mentioned?"],
            raw_text=None
        )

    @patch('api.server.run')
    def test_ping_endpoint_with_raw_text(self, mock_run, client):
        """Test ping endpoint with raw text."""
        mock_run.return_value = {
            "keywords_found": ["phishing"],
            "positive_analyst_questions": []
        }
        
        request_data = {
            "raw_text": "Blog post content about phishing attacks...",
            "keywords": ["phishing", "email"]
        }
        
        response = client.post("/api/v1/ping", json=request_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["url"] is None
        assert response_data["keywords_found"] == ["phishing"]
        
        mock_run.assert_called_once_with(
            url=None,
            ping=True,
            keywords=["phishing", "email"],
            analyst_questions=[],
            raw_text="Blog post content about phishing attacks..."
        )

    @patch('api.server.run')
    def test_ping_endpoint_error(self, mock_run, client):
        """Test ping endpoint when backend raises an error."""
        mock_run.side_effect = Exception("Backend processing failed")
        
        request_data = {"url": "https://example.com/blog"}
        
        response = client.post("/api/v1/ping", json=request_data)
        
        assert response.status_code == 500
        assert "Internal Server Error" in response.json()["detail"]


class TestAnalyzeEndpoint:
    """Test cases for the analyze endpoint."""

    @patch('api.server.run_in_threadpool')
    def test_analyze_endpoint_success(self, mock_run_in_threadpool, client):
        """Test successful analyze endpoint call."""
        # Setup mock
        mock_run_in_threadpool.return_value = {
            "keywords_found": ["malware", "trojan"],
            "qna": [
                {"question": "What is the main threat?", "answer": "Trojan malware"}
            ],
            "iocs_found": [
                {"type": "IP Address", "value": "192.168.1.100"},
                {"type": "Domain or URL", "value": "https://malicious.com"}
            ],
            "mitre_ttps": [
                {"id": "T1055", "name": "Process Injection", "confidence": 0.85}
            ]
        }
        
        request_data = {
            "url": "https://example.com/threat-analysis",
            "keywords": ["malware"],
            "analyst_questions": ["What threats are present?"]
        }
        
        response = client.post("/api/v1/analyze", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["url"] == "https://example.com/threat-analysis"
        assert response_data["keywords_found"] == ["malware", "trojan"]
        assert len(response_data["qna"]) == 1
        assert len(response_data["iocs_found"]) == 2
        assert len(response_data["mitre_ttps"]) == 1

    @patch('api.server.run_in_threadpool')
    def test_analyze_endpoint_error(self, mock_run_in_threadpool, client):
        """Test analyze endpoint when backend raises an error."""
        mock_run_in_threadpool.side_effect = Exception("Analysis failed")
        
        request_data = {"url": "https://example.com/blog"}
        
        response = client.post("/api/v1/analyze", json=request_data)
        
        assert response.status_code == 500
        assert "Internal Server Error" in response.json()["detail"]

    def test_analyze_endpoint_invalid_request(self, client):
        """Test analyze endpoint with invalid request data."""
        request_data = {
            "url": "https://example.com",
            "raw_text": "Some text"  # Both URL and text provided - should fail
        }
        
        response = client.post("/api/v1/analyze", json=request_data)
        
        assert response.status_code == 400
        assert "cannot be provided simultaneously" in response.json()["detail"]


class TestFeedbackEndpoint:
    """Test cases for the feedback endpoint."""

    def test_feedback_endpoint_success(self, client):
        """Test successful feedback submission."""
        request_data = {
            "url": "https://example.com/blog",
            "feedback_type": "accuracy",
            "context": "IoC extraction quality",
            "value": 1
        }
        
        response = client.post("/api/v1/feedback", json=request_data)
        
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

    def test_feedback_endpoint_negative_feedback(self, client):
        """Test submitting negative feedback."""
        request_data = {
            "url": "https://example.com/blog",
            "feedback_type": "false_positive",
            "context": "Incorrectly identified IoC",
            "value": -1
        }
        
        response = client.post("/api/v1/feedback", json=request_data)
        
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

    def test_feedback_endpoint_invalid_data(self, client):
        """Test feedback endpoint with missing required fields."""
        request_data = {
            "url": "https://example.com/blog"
            # Missing required fields
        }
        
        response = client.post("/api/v1/feedback", json=request_data)
        
        assert response.status_code == 422  # Validation error