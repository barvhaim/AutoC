"""Unit tests for string utility functions."""

import pytest
from backend.utils.str_utils import is_md5, is_sha256


class TestStringUtilities:
    """Test cases for string utility functions."""

    def test_is_md5_valid_hashes(self):
        """Test is_md5 with valid MD5 hashes."""
        valid_md5_hashes = [
            "471d596dad7ca027a44b21f3c3a2a0d9",
            "d41d8cd98f00b204e9800998ecf8427e",  # empty string MD5
            "098f6bcd4621d373cade4e832627b4f6",  # "test" MD5
            "ABCDEF1234567890ABCDEF1234567890",  # uppercase
            "abcdef1234567890abcdef1234567890",  # lowercase
        ]
        
        for hash_value in valid_md5_hashes:
            assert is_md5(hash_value), f"Expected {hash_value} to be valid MD5"

    def test_is_md5_invalid_hashes(self):
        """Test is_md5 with invalid MD5 hashes."""
        invalid_md5_hashes = [
            "",  # empty string
            "471d596dad7ca027a44b21f3c3a2a0d",  # too short (31 chars)
            "471d596dad7ca027a44b21f3c3a2a0d9a",  # too long (33 chars)
            "471d596dad7ca027a44b21f3c3a2a0dg",  # invalid character 'g'
            "471d596dad7ca027a44b21f3c3a2a0d9!",  # special character
            "not_a_hash",
            "12345",
            "G" * 32,  # all invalid characters
        ]
        
        for hash_value in invalid_md5_hashes:
            assert not is_md5(hash_value), f"Expected {hash_value} to be invalid MD5"

    def test_is_sha256_valid_hashes(self):
        """Test is_sha256 with valid SHA256 hashes."""
        valid_sha256_hashes = [
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # empty string SHA256
            "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",  # "test" SHA256
            "ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890",  # uppercase
            "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",  # lowercase
        ]
        
        for hash_value in valid_sha256_hashes:
            assert is_sha256(hash_value), f"Expected {hash_value} to be valid SHA256"

    def test_is_sha256_invalid_hashes(self):
        """Test is_sha256 with invalid SHA256 hashes."""
        invalid_sha256_hashes = [
            "",  # empty string
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85",  # too short (63 chars)
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855a",  # too long (65 chars)
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85g",  # invalid character 'g'
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85!",  # special character
            "not_a_hash",
            "12345",
            "G" * 64,  # all invalid characters
        ]
        
        for hash_value in invalid_sha256_hashes:
            assert not is_sha256(hash_value), f"Expected {hash_value} to be invalid SHA256"

    def test_is_md5_type_errors(self):
        """Test is_md5 with non-string inputs."""
        with pytest.raises(TypeError):
            is_md5(None)
        with pytest.raises(TypeError):
            is_md5(123)
        with pytest.raises(TypeError):
            is_md5([])

    def test_is_sha256_type_errors(self):
        """Test is_sha256 with non-string inputs."""
        with pytest.raises(TypeError):
            is_sha256(None)
        with pytest.raises(TypeError):
            is_sha256(123)
        with pytest.raises(TypeError):
            is_sha256([])