import { IOCTypeBackend } from "./consts.ts";

const toBase64Url = (input: string): string => {
  // Convert string to UTF-8 byte array
  const utf8Bytes = new TextEncoder().encode(input);

  // Convert byte array to regular base64
  const base64 = btoa(String.fromCharCode(...utf8Bytes));

  // Convert base64 to base64url (used by VirusTotal)
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
};

/**
 * Generates a VirusTotal URL for a given IOC type and value.
 * @param iocType - The type of IOC (backend type names like "SHA256 Hash", "IP Address")
 * @param iocValue - The value of the IOC
 * @returns The VirusTotal URL or an empty string if type is unsupported
 */
export const getVirusTotalUrl = (iocType: string, iocValue: string): string => {
  if (!iocType || !iocValue) return "";
  const baseUrl = "https://www.virustotal.com/gui/search/";

  if (iocType === IOCTypeBackend.URL) {
    // Encode URL in base64url format as required by VirusTotal
    const base64Url = toBase64Url(iocValue);
    return `https://www.virustotal.com/gui/url/${base64Url}/detection`;
  }

  // Supported types that use the same search pattern
  const supportedTypes = [
    IOCTypeBackend.IP,
    IOCTypeBackend.MD5,
    IOCTypeBackend.SHA256,
  ];
  if (supportedTypes.includes(iocType as typeof IOCTypeBackend.IP)) {
    return `${baseUrl}${encodeURIComponent(iocValue)}`;
  }

  // Unknown or unsupported type
  return "";
};
