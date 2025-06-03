// Utility functions for exporting IoCs in STIX format
import {IOCItem} from '../components/IOCsTable/IOCsTable';

interface StixObject {
  type: string;
  spec_version: string;
  id: string;
  created: string;
  modified: string;
  [key: string]: any;
}

interface StixBundle {
  type: string;
  id: string;
  spec_version: string;
  objects: StixObject[];
}

/**
 * Maps IoC types to STIX cyber observable types
 */
const mapIoCTypeToStixType = (iocType: string): string => {
  const typeMapping: Record<string, string> = {
    'ip': 'ipv4-addr',
    'ipv4': 'ipv4-addr',
    'ipv6': 'ipv6-addr',
    'domain': 'domain-name',
    'url': 'url',
    'email': 'email-addr',
    'md5': 'file',
    'sha1': 'file',
    'sha256': 'file',
    'hash': 'file'
  };

  return typeMapping[iocType.toLowerCase()] || 'indicator';
};

/**
 * Creates a unique STIX ID for an object
 */
const createStixId = (type: string): string => {
  const uuid = self.crypto.randomUUID();
  return `${type}--${uuid}`;
};

/**
 * Converts an IoC to a STIX cyber observable object
 */
const iocToStixObject = (ioc: IOCItem): StixObject => {
  const timestamp = new Date().toISOString();
  const stixType = mapIoCTypeToStixType(ioc.type);

  // Base STIX object structure
  const stixObject: StixObject = {
    type: stixType,
    spec_version: '2.1',
    id: createStixId(stixType),
    created: timestamp,
    modified: timestamp,
  };

  // Add specific properties based on the type
  switch (stixType) {
    case 'ipv4-addr':
    case 'ipv6-addr':
      stixObject.value = ioc.value;
      break;
    case 'domain-name':
      stixObject.value = ioc.value;
      break;
    case 'url':
      stixObject.value = ioc.value;
      break;
    case 'email-addr':
      stixObject.value = ioc.value;
      break;
    case 'file':
      // Handle hash values
      const hashType = ioc.type.toLowerCase();
      stixObject.hashes = {};
      if (['md5', 'sha1', 'sha256'].includes(hashType)) {
        stixObject.hashes[hashType] = ioc.value;
      } else {
        // Default to SHA-256 if the specific hash type isn't known
        stixObject.hashes['SHA-256'] = ioc.value;
      }
      break;
    default:
      // Default to indicator type for unknown IoC types
      stixObject.type = 'indicator';
      stixObject.pattern = `[file:hashes.'${ioc.type.toUpperCase()}' = '${ioc.value}']`;
      stixObject.pattern_type = 'stix';
      stixObject.valid_from = timestamp;
      break;
  }

  return stixObject;
};

/**
 * Converts an array of IoCs to a STIX bundle
 */
export const convertIocsToStixBundle = (iocs: IOCItem[]): StixBundle => {
  // Create STIX objects from IoCs
  const stixObjects = iocs.map(ioc => iocToStixObject(ioc));

  // Create the STIX bundle
    return {
      type: 'bundle',
      id: `bundle--${self.crypto.randomUUID()}`,
      spec_version: '2.1',
      objects: stixObjects,
  };
};

/**
 * Exports IoCs as a STIX bundle JSON file
 */
export const exportToStix = (iocs: IOCItem[], filename = 'iocs_stix_export.json'): void => {
  const stixBundle = convertIocsToStixBundle(iocs);

  // Create JSON blob and download
  const jsonContent = JSON.stringify(stixBundle, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
