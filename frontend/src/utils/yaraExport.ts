import { saveAs } from "file-saver";
import { IOCItem } from "../components/IOCsTable/IOCsTable";

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
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  let yaraContent = `rule IOCs_Export_${timestamp} {
  meta:
    description = "Auto-generated YARA rule from exported IOCs"
    author = "AutoC"
    date = "${new Date().toISOString().split("T")[0]}"
  
  strings:\n`;

  // Add each IOC as a string
  let stringCounter = 1;
  Object.entries(iocsByType).forEach(([type, values]) => {
    yaraContent += `    /* ${type} IOCs */\n`;

    values.forEach((value) => {
      // Escape any double quotes in the value
      const escapedValue = value.replace(/"/g, '\\"');
      yaraContent += `    $${type}_${stringCounter} = "${escapedValue}"\n`;
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
