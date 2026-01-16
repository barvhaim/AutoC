// Backend IOC type values (from backend/data_model/ioc.py IOCType enum)
export const IOCTypeBackend = {
  URL: "Domain or URL",
  IP: "IP Address",
  MD5: "MD5 Hash",
  SHA256: "SHA256 Hash",
  CHROME_EXTENSION: "Chrome Extension ID",
  BITCOIN_WALLET_ADDRESS: "Bitcoin Wallet Address",
} as const;

// Maps backend type names to short display names for charts
export const IOCType: Record<string, string> = {
  [IOCTypeBackend.URL]: "URL",
  [IOCTypeBackend.IP]: "IP",
  [IOCTypeBackend.MD5]: "MD5",
  [IOCTypeBackend.SHA256]: "SHA256",
  [IOCTypeBackend.CHROME_EXTENSION]: "CHROME_EXTENSION",
  [IOCTypeBackend.BITCOIN_WALLET_ADDRESS]: "BITCOIN_WALLET_ADDRESS",
};
