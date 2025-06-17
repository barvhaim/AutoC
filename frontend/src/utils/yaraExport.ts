import { saveAs } from "file-saver";
import { IOCItem } from "../components/IOCsTable/IOCsTable";

/**
 * Sanitizes IOC type names to ensure they are valid YARA identifiers
 * YARA identifiers can only contain alphanumeric and underscore characters
 * @param type The IOC type to sanitize
 * @returns Sanitized type name that can be used in YARA rules
 */
const sanitizeType = (type: string): string => {
  // Replace spaces and special characters with underscores
  // Remove any characters that aren't alphanumeric or underscore
  return type
    .toLowerCase()
    .replace(/\s+/g, "_")
    .replace(/[^a-z0-9_]/g, "")
    .replace(/^(\d)/, "ioc_$1"); // Ensure identifier doesn't start with a digit
};

/**
 * Generates and exports IOCs in YARA rule format
 * @param iocs List of IOC items to convert to YARA rule
 */
export const exportToYara = (iocs: IOCItem[]): void => {
  // Group IOCs by type
  const iocsByType: Record<string, string[]> = {};

  iocs.forEach((ioc) => {
    if (!iocsByType[ioc.type]) {
      iocsByType[ioc.type] = [];
    }
    iocsByType[ioc.type].push(ioc.value);
  });

  // Generate YARA rule content
  const timestamp = new Date().toISOString().replace(/\W/g, "_");
  let yaraContent = `rule IOCs_Export_${timestamp} {
  meta:
    description = "Auto-generated YARA rule from exported IOCs"
    author = "AutoC"
    date = "${new Date().toISOString().split("T")[0]}"
  
  strings:\n`;

  // Add each IOC as a string
  Object.entries(iocsByType).forEach(([type, values]) => {
    let stringCounter = 1; // Reset counter for each type
    const sanitizedType = sanitizeType(type);
    yaraContent += `    /* ${sanitizedType} IOCs */\n`;

    values.forEach((value) => {
      // Escape any double quotes in the value
      const escapedValue = value.replace(/"/g, '\\"');
      yaraContent += `    $${sanitizedType}_${stringCounter} = "${escapedValue}"\n`;
      stringCounter++;
    });

    yaraContent += "\n";
  });

  // Add condition section
  yaraContent += "  condition:\n";
  yaraContent += "    any of them\n";
  yaraContent += "}";

  // Create and download the file
  const blob = new Blob([yaraContent], { type: "text/plain;charset=utf-8" });
  saveAs(blob, `iocs_yara_rule_${timestamp}.yar`);
};
