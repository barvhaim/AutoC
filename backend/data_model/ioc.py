"""IOC data models and type definitions."""

from enum import Enum

from pydantic import BaseModel


class IOCType(str, Enum):
    URL = "Domain or URL"
    IP = "IP Address"
    MD5 = "MD5 Hash"
    SHA256 = "SHA256 Hash"
    CHROME_EXTENSION = "Chrome Extension ID"
    BITCOIN_WALLET_ADDRESS = "Bitcoin Wallet Address"


class IOC(BaseModel):
    type: IOCType
    value: str
