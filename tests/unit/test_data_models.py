"""Unit tests for data models."""

import pytest
from pydantic import ValidationError
from backend.data_model.ioc import IOC, IOCType
from api.data_models import AnalyzeRequest, FeedbackRequest


class TestIOCDataModel:
    """Test cases for IOC data model."""

    def test_ioc_creation_valid(self):
        """Test creating IOC instances with valid data."""
        test_cases = [
            (IOCType.IP, "192.168.1.1"),
            (IOCType.URL, "https://malicious-site.com"),
            (IOCType.MD5, "471d596dad7ca027a44b21f3c3a2a0d9"),
            (IOCType.SHA256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            (IOCType.CHROME_EXTENSION, "abcdefghijklmnopqrstuvwxyz123456"),
            (IOCType.BITCOIN_WALLET_ADDRESS, "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
        ]
        
        for ioc_type, value in test_cases:
            ioc = IOC(type=ioc_type, value=value)
            assert ioc.type == ioc_type
            assert ioc.value == value

    def test_ioc_type_enum_values(self):
        """Test IOCType enum values."""
        assert IOCType.URL == "Domain or URL"
        assert IOCType.IP == "IP Address"
        assert IOCType.MD5 == "MD5 Hash"
        assert IOCType.SHA256 == "SHA256 Hash"
        assert IOCType.CHROME_EXTENSION == "Chrome Extension ID"
        assert IOCType.BITCOIN_WALLET_ADDRESS == "Bitcoin Wallet Address"

    def test_ioc_serialization(self):
        """Test IOC model serialization."""
        ioc = IOC(type=IOCType.IP, value="192.168.1.1")
        data = ioc.model_dump()
        
        assert data == {
            "type": "IP Address",
            "value": "192.168.1.1"
        }

    def test_ioc_invalid_type(self):
        """Test IOC creation with invalid type."""
        with pytest.raises(ValidationError):
            IOC(type="INVALID_TYPE", value="some_value")


class TestAnalyzeRequest:
    """Test cases for AnalyzeRequest data model."""

    def test_analyze_request_with_url(self):
        """Test creating AnalyzeRequest with URL."""
        request = AnalyzeRequest(
            url="https://example.com/blog-post",
            keywords=["malware", "threat"],
            analyst_questions=["What IoCs are present?"]
        )
        
        assert str(request.url) == "https://example.com/blog-post"
        assert request.keywords == ["malware", "threat"]
        assert request.analyst_questions == ["What IoCs are present?"]
        assert request.raw_text is None

    def test_analyze_request_with_raw_text(self):
        """Test creating AnalyzeRequest with raw text."""
        raw_text = "This is a sample blog post with malware indicators."
        request = AnalyzeRequest(
            raw_text=raw_text,
            keywords=["malware"],
            analyst_questions=[]
        )
        
        assert request.url is None
        assert request.raw_text == raw_text
        assert request.keywords == ["malware"]
        assert request.analyst_questions == []

    def test_analyze_request_minimal(self):
        """Test creating AnalyzeRequest with minimal data."""
        request = AnalyzeRequest()
        
        assert request.url is None
        assert request.raw_text is None
        assert request.keywords is None
        assert request.analyst_questions is None

    def test_analyze_request_invalid_url(self):
        """Test AnalyzeRequest with invalid URL."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(url="not_a_valid_url")

    def test_analyze_request_serialization(self):
        """Test AnalyzeRequest serialization."""
        request = AnalyzeRequest(
            url="https://example.com",
            keywords=["test"],
            analyst_questions=["question?"]
        )
        
        data = request.model_dump()
        
        # Check individual fields rather than exact dict match due to HttpUrl type
        assert str(data["url"]) == "https://example.com/"
        assert data["keywords"] == ["test"]
        assert data["analyst_questions"] == ["question?"]
        assert data["raw_text"] is None


class TestFeedbackRequest:
    """Test cases for FeedbackRequest data model."""

    def test_feedback_request_creation(self):
        """Test creating FeedbackRequest with valid data."""
        request = FeedbackRequest(
            url="https://example.com/blog",
            feedback_type="accuracy",
            context="IoC extraction quality",
            value=1
        )
        
        assert request.url == "https://example.com/blog"
        assert request.feedback_type == "accuracy"
        assert request.context == "IoC extraction quality"
        assert request.value == 1

    def test_feedback_request_negative_value(self):
        """Test FeedbackRequest with negative feedback."""
        request = FeedbackRequest(
            url="https://example.com/blog",
            feedback_type="relevance",
            context="False positive detection",
            value=-1
        )
        
        assert request.value == -1

    def test_feedback_request_serialization(self):
        """Test FeedbackRequest serialization."""
        request = FeedbackRequest(
            url="https://example.com",
            feedback_type="test",
            context="test context",
            value=1
        )
        
        data = request.model_dump()
        expected = {
            "url": "https://example.com",
            "feedback_type": "test",
            "context": "test context",
            "value": 1
        }
        
        assert data == expected

    def test_feedback_request_required_fields(self):
        """Test FeedbackRequest with missing required fields."""
        with pytest.raises(ValidationError):
            FeedbackRequest()  # All fields are required