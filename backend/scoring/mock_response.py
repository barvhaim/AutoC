"""Mock response data for testing purposes."""

mock_response = {
    "url": "https://securityintelligence.com/posts/gozi-strikes-again-targeting-banks-cryptocurrency-and-more",
    "keywords_found": [
        "spyeye",
        "bank",
        "malicious",
        "analysis",
        "transaction",
        "passwords",
        "grabber",
        "cryptocurrency",
        "cybercrime",
        "ursnif",
        "threat",
        "zeus",
        "fraud",
        "phishing",
        "spyware",
        "intelligence",
        "gozi",
        "wallet",
    ],
    "qna": [
        {
            "question": "Does the malware using web inject?",
            "answer": "Yes, the Gozi malware uses web injects to modify the content of legitimate websites, making them appear genuine to unsuspecting users.",
        },
        {
            "question": "Is there credential theft from the browser?",
            "answer": "Yes, Gozi malware uses web injects to trick users into entering their credentials and financial information, allowing for credential theft from the browser.",
        },
        {
            "question": "Does the malware install malicious chrome extension?",
            "answer": "The answer cannot be determined from the provided context.",
        },
        {
            "question": "Does is steals credit cards or bank information?",
            "answer": "Yes, Gozi malware is designed to steal sensitive information, including bank login credentials, credit card numbers, and other financial data, by using web injects to trick users into entering their credentials on fake login pages.",
        },
        {
            "question": "Is it related to wallet stealer?",
            "answer": "Gozi malware is related to stealing login credentials, including those for cryptocurrency wallets and exchanges, but it is not specifically a wallet stealer. It uses web injects to trick users into entering their credentials and financial information.",
        },
        {
            "question": "What kind of information the malware steals?",
            "answer": "The Gozi malware steals login credentials, including usernames, passwords, and two-factor authentication codes, from banks, financial services, and cryptocurrency platforms, allowing cybercriminals to gain unauthorized access to user accounts.",
        },
        {
            "question": "Where does it forward the stolen information?",
            "answer": "The answer cannot be determined from the provided context.",
        },
        {
            "question": "What are the targeted located (regions, banks name, wallets)?",
            "answer": "The targeted locations include Asia, with a focus on Italian banks, and various companies associated with cryptocurrency, such as cryptocurrency exchanges, wallets, and blockchain service providers. Specific targets are not detailed, but a previous report covered Gozi's campaign targeted at Italian banks.",
        },
    ],
    "iocs_found": [
        {"type": "URL", "value": "hxxps://gestorbancasrl.com"},
        {"type": "URL", "value": "hxxps://gestorbancosrl.com"},
        {"type": "URL", "value": "hxxps://avas1ta.com/in"},
        {"type": "URL", "value": "hxxps://avas1t.de/in"},
        {"type": "URL", "value": "hxxps://njamma.com"},
        {"type": "URL", "value": "hxxps://itgjmfgdzxcv.com"},
        {"type": "URL", "value": "https://PowerHost[.]ro"},
    ],
}
