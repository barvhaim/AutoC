export const cleanIocValue = (value: string): string => {
  // Replace "[.]" with "." from the value of urls and IPs
  let cleanedValue = value.replace(/\[\.\]/g, ".");
  /// Replace "hxxps://" with "https://" in the cleaned value
  cleanedValue = cleanedValue.replace(/hxxps:\/\//g, "https://");
  // Replace "hxxp://" with "http://" in the cleaned value
  cleanedValue = cleanedValue.replace(/hxxp:\/\//g, "http://");
  return cleanedValue;
};
