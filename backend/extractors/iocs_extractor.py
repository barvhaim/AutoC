"""Given an article, extract IOCs from the content"""

import logging
import os
from typing import Any, List

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableSequence
from backend.prompts import get_prompts
from backend.llm import get_chat_llm_client
from backend.data_model.ioc import IOC, IOCType

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IOCsExtractor:
    # IOC type definitions for prompt generation
    # Maps IOCType enum to detailed extraction instructions
    IOC_DEFINITIONS = {
        IOCType.URL: """<Domain or URL>
Full or obfuscated web addresses (URLs, domains, or hostnames)
Examples: https://example.com, hxxps://bad[.]com, malicious.net, evil[.]com
MUST contain domain names or URL patterns
MUST NOT be plain IP addresses (no 192.168.1.1 format)
</Domain or URL>""",
        IOCType.IP: """<IP Address>
ONLY IPv4 or IPv6 addresses in numeric format
Examples: 192.168.1.1, 10.0.0.1, 2001:0db8:85a3::8a2e:0370:7334
MUST be numeric IP addresses only
MUST NOT include URLs, domains, or hostnames
</IP Address>""",
        IOCType.MD5: """<MD5 Hash>
ONLY 32-character hexadecimal hashes
Example: 5d41402abc4b2a76b9719d911017c592
Must be exactly 32 hex characters (0-9, a-f)
</MD5 Hash>""",
        IOCType.SHA256: """<SHA256 Hash>
ONLY 64-character hexadecimal hashes
Example: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
Must be exactly 64 hex characters (0-9, a-f)
</SHA256 Hash>""",
        IOCType.CHROME_EXTENSION: """<Chrome Extension ID>
ONLY Chrome extension IDs (32-character lowercase alphanumeric)
Example: cjpalhdlnbpafiamejdnhcphjbkeiagm
Must be exactly 32 characters, lowercase letters and numbers only
</Chrome Extension ID>""",
        IOCType.BITCOIN_WALLET_ADDRESS: """<Bitcoin Wallet Address>
ONLY Bitcoin wallet addresses (26-35 alphanumeric characters)
Example: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
Typically starts with 1, 3, or bc1
</Bitcoin Wallet Address>""",
    }

    def __init__(self, article_content: str):
        self.article_content = article_content
        self.prompts = get_prompts()

    @staticmethod
    def _llm() -> Any:
        model_name = os.getenv("LLM_MODEL", "meta-llama/llama-3-3-70b-instruct")

        return get_chat_llm_client(
            model_name=model_name,
            model_parameters={
                "decoding_method": "sample",
                "temperature": 0,
                "max_tokens": 4096,
            },
        )

    @staticmethod
    def _json_escaping(response: AIMessage) -> AIMessage:
        """Clean and prepare LLM response for JSON parsing"""
        content = response.content

        # Log the raw response for debugging
        logger.info("Raw LLM response (first 500 chars): %s", content[:500])

        # Remove markdown code blocks if present
        if content.startswith("```"):
            # Remove opening code block
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            # Remove closing code block
            if content.endswith("```"):
                content = (
                    content.rsplit("\n", 1)[0] if "\n" in content else content[:-3]
                )

        # Strip whitespace
        content = content.strip()

        # Handle empty responses - convert to empty JSON array
        if not content or content == "":
            logger.info("Empty LLM response, converting to empty array []")
            content = "[]"

        # Log the cleaned content for debugging
        logger.info("Cleaned LLM response (first 500 chars): %s", content[:500])

        # Handle escaped backslashes
        content = content.replace("\\", "\\\\")

        return AIMessage(content=content)

    @staticmethod
    def _response_to_iocs(iocs_response: List[str], ioc_type: IOCType) -> List[IOC]:
        return [IOC(type=ioc_type, value=o) for o in iocs_response]

    def _extract_ioc(self, ioc_type: IOCType) -> RunnableSequence:
        llm = self._llm()

        # Get the definition for this IOC type
        ioc_definition = self.IOC_DEFINITIONS.get(
            ioc_type, f"Extract {ioc_type.value} indicators"
        )

        system_message = SystemMessagePromptTemplate.from_template(
            template=self.prompts["iocs"]["system"],
            partial_variables={
                "ioc_type": ioc_type.value,
                "ioc_definition": ioc_definition,
                "context": self.article_content,
            },
        )
        # More explicit user message to reinforce JSON-only output
        user_message = HumanMessage(content="Output the JSON array now:")
        messages = [system_message, user_message]

        prompt = ChatPromptTemplate.from_messages(messages=messages)

        def safe_parse_and_convert(response):
            """Safely parse JSON and convert to IOCs with error logging"""
            try:
                parsed = JsonOutputParser().parse(response.content)
                return self._response_to_iocs(parsed, ioc_type)
            except Exception as e:
                logger.error("Failed to parse JSON for %s", ioc_type.value)
                logger.error("Raw response content: %s", response.content)
                logger.error("Error: %s", str(e))
                raise

        return prompt | llm | self._json_escaping | safe_parse_and_convert

    def extract_iocs_from_text(self) -> List[IOC]:
        iocs, val_l = [], []
        tasks = {
            IOCType.URL.name: self._extract_ioc(IOCType.URL),
            IOCType.IP.name: self._extract_ioc(IOCType.IP),
            IOCType.MD5.name: self._extract_ioc(IOCType.MD5),
            IOCType.SHA256.name: self._extract_ioc(IOCType.SHA256),
            IOCType.CHROME_EXTENSION.name: self._extract_ioc(IOCType.CHROME_EXTENSION),
        }
        res = RunnableParallel(**tasks).invoke(input={})

        # make sure we remove duplicate iocs
        for ioc_of_type in res.values():
            for ioc in ioc_of_type:
                if ioc.value not in val_l:
                    iocs.append(ioc)
                    val_l.append(ioc.value)
        return iocs
