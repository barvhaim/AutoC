"""Example showing how to use the AutoC API endpoints."""

import requests
import json
from typing import Dict, Any


def api_analyze_example():
    """Example: Using the /analyze API endpoint."""
    print("=" * 50)
    print("AutoC API Example: Analyze Endpoint")
    print("=" * 50)
    
    # API endpoint (assuming local development server)
    url = "http://localhost:8000/api/v1/analyze"
    
    # Request payload
    payload = {
        "url": "https://example.com/security-blog",
        "keywords": ["malware", "phishing", "IoC"],
        "analyst_questions": [
            "What are the main threats discussed?",
            "Are there any IoCs mentioned?",
            "What defensive measures are recommended?"
        ]
    }
    
    print(f"Making request to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("\nAnalysis Results:")
            print(f"Keywords found: {result.get('keywords_found', [])}")
            print(f"IoCs found: {len(result.get('iocs_found', []))}")
            print(f"Q&A pairs: {len(result.get('qna', []))}")
            print(f"MITRE TTPs: {len(result.get('mitre_ttps', []))}")
            
            # Display some IoCs
            for ioc in result.get('iocs_found', [])[:3]:  # Show first 3
                print(f"  IoC: {ioc['type']} - {ioc['value']}")
                
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed (expected if server not running): {e}")


def api_ping_example():
    """Example: Using the /ping API endpoint."""
    print("\n" + "=" * 50)
    print("AutoC API Example: Ping Endpoint")
    print("=" * 50)
    
    url = "http://localhost:8000/api/v1/ping"
    
    payload = {
        "url": "https://example.com/quick-check",
        "keywords": ["threat", "malware"],
        "analyst_questions": ["Is this content security-related?"]
    }
    
    print(f"Making ping request to: {url}")
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print("\nPing Results:")
            print(f"URL: {result.get('url')}")
            print(f"Keywords found: {result.get('keywords_found', [])}")
            print(f"Positive questions: {len(result.get('positive_analyst_questions', []))}")
            
        else:
            print(f"Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed (expected if server not running): {e}")


def api_raw_text_example():
    """Example: Analyzing raw text via API."""
    print("\n" + "=" * 50)
    print("AutoC API Example: Raw Text Analysis")
    print("=" * 50)
    
    url = "http://localhost:8000/api/v1/analyze"
    
    # Sample text with IoCs
    sample_text = """
    Incident Report: Advanced Persistent Threat Activity
    
    Our security team detected suspicious network activity originating from:
    - Command & Control server: 203.0.113.42
    - Malicious domain: evil-c2.badactor.net
    - Phishing site: https://fake-bank.phishing-domain.com/login
    
    Malware samples identified:
    - File hash (MD5): d41d8cd98f00b204e9800998ecf8427e
    - File hash (SHA256): a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
    
    The attack chain involves credential theft and lateral movement techniques.
    """
    
    payload = {
        "raw_text": sample_text,
        "keywords": ["APT", "malware", "phishing", "credential theft"],
        "analyst_questions": [
            "What IoCs are present in this report?",
            "What attack techniques are described?"
        ]
    }
    
    print("Analyzing raw text content...")
    print(f"Text preview: {sample_text[:150]}...")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("\nRaw Text Analysis Results:")
            print(f"Keywords found: {result.get('keywords_found', [])}")
            print(f"IoCs extracted: {len(result.get('iocs_found', []))}")
            
            # Show extracted IoCs
            print("\nExtracted IoCs:")
            for ioc in result.get('iocs_found', []):
                print(f"  {ioc['type']}: {ioc['value']}")
                
            # Show Q&A
            print("\nGenerated Q&A:")
            for qa in result.get('qna', []):
                print(f"  Q: {qa['question']}")
                print(f"  A: {qa['answer'][:100]}...")
                print()
                
        else:
            print(f"Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed (expected if server not running): {e}")


def api_feedback_example():
    """Example: Submitting feedback via API."""
    print("\n" + "=" * 50)
    print("AutoC API Example: Feedback Submission")
    print("=" * 50)
    
    url = "http://localhost:8000/api/v1/feedback"
    
    # Positive feedback
    feedback_payload = {
        "url": "https://example.com/analyzed-blog",
        "feedback_type": "accuracy",
        "context": "IoC extraction was very accurate",
        "value": 1  # 1 for positive, -1 for negative
    }
    
    print("Submitting positive feedback...")
    
    try:
        response = requests.post(url, json=feedback_payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Feedback submitted: {result}")
        else:
            print(f"Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed (expected if server not running): {e}")
    
    # Negative feedback example
    print("\nSubmitting negative feedback...")
    
    negative_feedback = {
        "url": "https://example.com/another-blog",
        "feedback_type": "false_positive",
        "context": "Incorrectly identified legitimate URL as malicious",
        "value": -1
    }
    
    try:
        response = requests.post(url, json=negative_feedback, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Negative feedback submitted: {result}")
        else:
            print(f"Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def check_server_health():
    """Check if the AutoC server is running."""
    print("=" * 50)
    print("AutoC API Example: Health Check")
    print("=" * 50)
    
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Server status: {result.get('status')}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Server not reachable: {e}")
        print("\nTo start the server, run:")
        print("  python -m uvicorn main:app --host 0.0.0.0 --port 8000")
        return False


def main():
    """Run all API examples."""
    print("AutoC API Usage Examples")
    print("========================")
    print()
    print("These examples demonstrate how to interact with the AutoC API.")
    print("Make sure the AutoC server is running on localhost:8000")
    print()
    
    # Check if server is running
    server_running = check_server_health()
    
    if not server_running:
        print("\nNote: Examples will show expected behavior even if server is not running.")
        print()
    
    # Run examples
    api_analyze_example()
    api_ping_example()
    api_raw_text_example()
    api_feedback_example()
    
    print("\n" + "=" * 50)
    print("API Examples completed!")
    print("For more information, see the API documentation.")
    print("=" * 50)


if __name__ == "__main__":
    main()