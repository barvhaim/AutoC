"""IOC enrichment module for threat intelligence data enhancement."""

import logging
import os
from typing import List, Optional

from dotenv import load_dotenv

from backend.data_model.ioc import IOC, IOCType
from backend.enrichment.vt_enrichment import VirusTotalEnrichment
from backend.utils.str_utils import is_md5, is_sha256

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")


class EnrichIOCs:
    def __init__(self, iocs: List[IOC]):
        self.iocs = iocs
        self.vt_enrichment = VirusTotalEnrichment() if VIRUSTOTAL_API_KEY else None

    @staticmethod
    def _detect_actual_ioc_type(ioc_val: str) -> Optional[IOCType]:
        """
        This function receives an IOC string that should be SHA256 or MD5 and detect which one is it
        If it fails then the function return None.
        """
        if is_sha256(ioc_val):
            return IOCType.SHA256
        if is_md5(ioc_val):
            return IOCType.MD5
        else:
            return None

    def enrich_iocs(self) -> List[IOC]:
        enriched_iocs = []
        for ioc in self.iocs:
            if ioc.type == IOCType.MD5 or ioc.type == IOCType.SHA256:
                ioc_actual_type = self._detect_actual_ioc_type(ioc_val=ioc.value)
                if not ioc_actual_type:  # ioc should be SHA256 or MD5
                    continue
                elif ioc_actual_type == IOCType.SHA256:
                    enriched_iocs.append(IOC(type=ioc_actual_type, value=ioc.value))
                elif ioc_actual_type == IOCType.MD5:
                    new_ioc = IOC(type=ioc_actual_type, value=ioc.value)
                    try:
                        if self.vt_enrichment:
                            sha256_hash = self.vt_enrichment.md5_to_sha256(
                                md5_hash=ioc.value
                            )
                            if sha256_hash:
                                ioc.value = (
                                    ioc.value + " (SHA256: " + str(sha256_hash) + ")"
                                )
                                new_ioc = IOC(type=IOCType.MD5, value=ioc.value)
                            enriched_iocs.append(new_ioc)
                    except:
                        enriched_iocs.append(new_ioc)
                else:
                    raise NotImplementedError(
                        f"wrong IOCTypeEnum was detected: {ioc_actual_type}"
                    )
            else:  # other IOC types such as URL/IP
                enriched_iocs.append(ioc)
        return enriched_iocs
