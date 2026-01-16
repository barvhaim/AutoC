"""VirusTotal enrichment module for IOC threat intelligence."""

import logging
import os
from typing import Dict

import diskcache as dc
import requests
from dotenv import load_dotenv
from backend.utils.str_utils import is_md5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


class VirusTotalEnrichment:
    def __init__(self):
        self.cache = dc.Cache("vt_md5_sha256_cache")
        self.api_key = os.getenv("VIRUSTOTAL_API_KEY")
        self.base_url = "https://www.virustotal.com/api/v3"

    def md5_to_sha256(self, md5_hash: str) -> Dict:
        """
        Enrich the given MD5 hash using the VirusTotal API.
        :param md5: The MD5 hash to enrich.
        :return: The VirusTotal response.
        """
        if not is_md5(md5_hash):
            raise ValueError("Invalid MD5 hash")

        if md5_hash in self.cache:
            return self.cache[md5_hash]

        url = f"{self.base_url}/files/{md5_hash}"
        headers = {"x-apikey": self.api_key}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            sha256_hash = (
                response.json().get("data", {}).get("attributes", {}).get("sha256")
            )
            if sha256_hash:
                self.cache[md5_hash] = sha256_hash
                return sha256_hash

        raise ValueError("SHA256 hash not found")


if __name__ == "__main__":
    _vt = VirusTotalEnrichment()
    _md5 = "471d596dad7ca027a44b21f3c3a2a0d9"
    _sha256 = _vt.md5_to_sha256(_md5)
    logger.info("SHA256 hash for MD5 %s: %s", _md5, _sha256)
