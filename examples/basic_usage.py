"""Example usage of AutoC for IoC extraction."""

import sys
import os

# Add the parent directory to the path so we can import from the project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def example_basic_usage():
    """Example: Basic usage with a URL."""
    print("=" * 50)
    print("AutoC Example: Basic URL Analysis")
    print("=" * 50)
    
    # Note: This would require proper environment setup with API keys
    # For demonstration purposes, we'll show the expected usage pattern
    
    # Example URL (this would need to be a real URL in practice)
    url = "https://example.com/security-blog-post"
    
    print(f"Analyzing URL: {url}")
    print("Note: This requires proper API key configuration in .env file")
    
    try:
        from backend.run import run
        
        # This would actually perform the analysis
        result = run(url=url)
        
        print(f"Keywords found: {result.get('keywords_found', [])}")
        print(f"Q&A pairs: {len(result.get('qna', []))}")
        print(f"IoCs found: {len(result.get('iocs_found', []))}")
        print(f"MITRE TTPs: {result.get('mitre_ttps', 'None')}")
        
    except ImportError as e:
        print(f"Import error (expected without full setup): {e}")
        print("This example would work with proper dependency installation:")
        print("  pip install -r requirements.txt")
        print("  # Configure .env file with API keys")
        print("  python examples/basic_usage.py")
        
        # Show expected output structure
        print("\nExpected output structure:")
        mock_result = {
            "keywords_found": ["malware", "threat", "security"],
            "qna": [
                {"question": "What threats are mentioned?", "answer": "Various malware families..."},
                {"question": "Are there IoCs?", "answer": "Yes, several IP addresses and domains"}
            ],
            "iocs_found": [
                {"type": "IP Address", "value": "192.168.1.100"},
                {"type": "Domain or URL", "value": "malicious-site.com"}
            ],
            "mitre_ttps": [
                {"id": "T1055", "name": "Process Injection", "confidence": 0.85}
            ]
        }
        print(f"Keywords found: {mock_result['keywords_found']}")
        print(f"Q&A pairs: {len(mock_result['qna'])}")
        print(f"IoCs found: {len(mock_result['iocs_found'])}")
        print(f"MITRE TTPs: {len(mock_result['mitre_ttps'])}")
        
    except Exception as e:
        print(f"Error (expected without proper setup): {e}")


def example_with_raw_text():
    """Example: Analyzing raw text content."""
    print("\n" + "=" * 50)
    print("AutoC Example: Raw Text Analysis")
    print("=" * 50)
    
    # Sample blog post content with IoCs
    raw_text = """
    Security Alert: New Malware Campaign Detected
    
    Our security team has identified a new malware campaign targeting financial institutions.
    The malware communicates with the following command and control servers:
    
    - 192.168.1.100 (suspicious IP address)
    - malware-c2.evil-domain.com (malicious domain)
    - https://phishing-site.badactor.net/login (phishing URL)
    
    The malware also drops files with the following hashes:
    - MD5: 471d596dad7ca027a44b21f3c3a2a0d9
    - SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    
    The attack uses techniques similar to APT groups and involves process injection
    and credential dumping activities.
    """
    
    print("Analyzing raw text content...")
    print("Sample content preview:")
    print(raw_text[:200] + "...")
    
    try:
        from backend.run import run
        
        result = run(raw_text=raw_text)
        
        print(f"Keywords found: {result.get('keywords_found', [])}")
        print(f"IoCs extracted: {len(result.get('iocs_found', []))}")
        
        # Display extracted IoCs
        for ioc in result.get('iocs_found', []):
            print(f"  - {ioc['type']}: {ioc['value']}")
            
    except ImportError as e:
        print(f"Import error (expected without full setup): {e}")
        print("\nExpected IoC extraction from the text:")
        expected_iocs = [
            {"type": "IP Address", "value": "192.168.1.100"},
            {"type": "Domain or URL", "value": "malware-c2.evil-domain.com"},
            {"type": "Domain or URL", "value": "https://phishing-site.badactor.net/login"},
            {"type": "MD5 Hash", "value": "471d596dad7ca027a44b21f3c3a2a0d9"},
            {"type": "SHA256 Hash", "value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
        ]
        print(f"Expected IoCs: {len(expected_iocs)}")
        for ioc in expected_iocs:
            print(f"  - {ioc['type']}: {ioc['value']}")
            
    except Exception as e:
        print(f"Error (expected without proper setup): {e}")


def example_with_custom_keywords():
    """Example: Using custom keywords for analysis."""
    print("\n" + "=" * 50)
    print("AutoC Example: Custom Keywords Analysis")
    print("=" * 50)
    
    # Custom keywords to look for
    custom_keywords = [
        "ransomware", "phishing", "malware", "botnet", 
        "APT", "threat actor", "exploit", "vulnerability"
    ]
    
    # Custom analyst questions
    analyst_questions = [
        "What type of malware is described?",
        "What are the main attack vectors?",
        "Are there any specific threat actors mentioned?",
        "What defensive measures are recommended?"
    ]
    
    print(f"Custom keywords: {custom_keywords}")
    print(f"Analyst questions: {len(analyst_questions)}")
    
    try:
        from backend.run import run
        
        result = run(
            url="https://example.com/threat-report",
            keywords=custom_keywords,
            analyst_questions=analyst_questions
        )
        
        print(f"Keywords found: {result.get('keywords_found', [])}")
        print(f"Q&A pairs generated: {len(result.get('qna', []))}")
        
        # Display Q&A pairs
        for qa in result.get('qna', []):
            print(f"Q: {qa['question']}")
            print(f"A: {qa['answer'][:100]}...")
            print()
            
    except ImportError as e:
        print(f"Import error (expected without full setup): {e}")
        print("\nExpected behavior:")
        print("- AutoC would analyze the URL content")
        print("- Look for the specified custom keywords")
        print("- Generate answers to the analyst questions")
        print("- Extract relevant IoCs and MITRE TTPs")
        
        mock_qna = [
            {"question": "What type of malware is described?", "answer": "The article describes a banking trojan that targets financial institutions..."},
            {"question": "What are the main attack vectors?", "answer": "Primary attack vectors include phishing emails and drive-by downloads..."}
        ]
        print(f"Example Q&A pairs: {len(mock_qna)}")
        for qa in mock_qna:
            print(f"Q: {qa['question']}")
            print(f"A: {qa['answer'][:100]}...")
            print()
            
    except Exception as e:
        print(f"Error (expected without proper setup): {e}")


def example_ping_mode():
    """Example: Using ping mode for quick analysis."""
    print("\n" + "=" * 50)
    print("AutoC Example: Ping Mode (Quick Analysis)")
    print("=" * 50)
    
    print("Ping mode provides quick analysis without full IoC extraction")
    
    try:
        from backend.run import run
        
        result = run(
            url="https://example.com/blog-post",
            ping=True,
            keywords=["malware", "phishing"],
            analyst_questions=["Are there any security threats mentioned?"]
        )
        
        print(f"Keywords found: {result.get('keywords_found', [])}")
        print(f"Positive analyst questions: {len(result.get('positive_analyst_questions', []))}")
        
    except ImportError as e:
        print(f"Import error (expected without full setup): {e}")
        print("\nPing mode expected behavior:")
        print("- Fast analysis without full IoC extraction")
        print("- Returns keywords and positive analyst question responses")
        print("- Useful for quick content relevance checking")
        
        mock_ping_result = {
            "keywords_found": ["malware", "phishing", "threat"],
            "positive_analyst_questions": [
                {"question": "Are there any security threats mentioned?", "answer": "Yes, several malware families are discussed"}
            ]
        }
        print(f"Keywords found: {mock_ping_result['keywords_found']}")
        print(f"Positive analyst questions: {len(mock_ping_result['positive_analyst_questions'])}")
        
    except Exception as e:
        print(f"Error (expected without proper setup): {e}")


def main():
    """Run all examples."""
    print("AutoC - Automated IoC Extraction Examples")
    print("=========================================")
    print()
    print("These examples demonstrate how to use AutoC for various analysis tasks.")
    print("Note: Proper API key configuration is required for actual usage.")
    print()
    
    example_basic_usage()
    example_with_raw_text()
    example_with_custom_keywords()
    example_ping_mode()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("For more information, see the README.md file.")
    print("=" * 50)


if __name__ == "__main__":
    main()