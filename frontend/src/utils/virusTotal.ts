import { IOCType } from "./consts.ts";

/**
 * Generates a VirusTotal URL for a given IOC type and value.
 * @param iocType - The type of IOC (URL, IP, MD5, SHA256)
 * @param iocValue - The value of the IOC
 * @returns The VirusTotal URL or an empty string if type is unsupported
 */
export const getVirusTotalUrl = (iocType: string, iocValue: string): string => {
  if (!iocType || !iocValue) return "";
  const baseUrl = "https://www.virustotal.com/gui/search/";

  if (iocType === IOCType.URL) {
    // Encode URL in base64url format as required by VirusTotal
    const base64Url = btoa(iocValue)
      .replace(/=+$/, "")
      .replace(/\+/g, "-")
      .replace(/\//g, "_");
    return `https://www.virustotal.com/gui/url/${base64Url}/detection`;
  }

  // Supported types that use the same search pattern
  const supportedTypes = [IOCType.IP, IOCType.MD5, IOCType.SHA256];
  if (supportedTypes.includes(iocType)) {
    return `${baseUrl}${encodeURIComponent(iocValue)}`;
  }

  // Unknown or unsupported type
  return "";
};
