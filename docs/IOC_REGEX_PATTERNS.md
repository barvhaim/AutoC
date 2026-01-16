# IOC Regex Patterns Research

## Overview
This document contains researched regex patterns for extracting various IOC types from threat intelligence text. These patterns will be used in the hybrid extraction system.

## Pattern Categories

### 1. Hash-based IOCs (High Confidence)

#### MD5 Hash
- **Pattern**: `\b[a-fA-F0-9]{32}\b`
- **Confidence**: Very High (99%+)
- **Characteristics**: Exactly 32 hexadecimal characters
- **False Positives**: Very rare (random 32-char hex strings)
- **Examples**:
  - `5d41402abc4b2a76b9719d911017c592`
  - `098f6bcd4621d373cade4e832627b4f6`

#### SHA-1 Hash
- **Pattern**: `\b[a-fA-F0-9]{40}\b`
- **Confidence**: Very High (99%+)
- **Characteristics**: Exactly 40 hexadecimal characters
- **Examples**:
  - `356a192b7913b04c54574d18c28d46e6395428ab`

#### SHA-256 Hash
- **Pattern**: `\b[a-fA-F0-9]{64}\b`
- **Confidence**: Very High (99%+)
- **Characteristics**: Exactly 64 hexadecimal characters
- **Examples**:
  - `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### 2. Network-based IOCs

#### IPv4 Address
- **Pattern**: `\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b`
- **Confidence**: High (90%+)
- **Characteristics**: Four octets (0-255) separated by dots
- **False Positives**: Version numbers (e.g., 1.2.3.4), dates
- **Context Filtering**: Exclude common private ranges in some contexts
- **Examples**:
  - `192.168.1.100`
  - `203.0.113.42`
  - `10.0.0.5`

#### IPv6 Address
- **Pattern**: `\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b|\b(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\b`
- **Confidence**: High (90%+)
- **Characteristics**: Eight groups of 4 hex digits separated by colons
- **Examples**:
  - `2001:0db8:85a3:0000:0000:8a2e:0370:7334`
  - `2001:db8::1`

#### Domain Names
- **Pattern**: `\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b`
- **Confidence**: Medium (70-80%)
- **Characteristics**: Valid domain structure with TLD
- **False Positives**: Email addresses, file extensions
- **Context Required**: Need to distinguish from legitimate domains
- **Examples**:
  - `malicious.com`
  - `evil.net`
  - `bad.site`

#### Defanged Domains/URLs
- **Pattern**: `\b(?:hxxp|hXXp|h\[xx\]p|http)s?://[^\s]+|\b[a-zA-Z0-9\-]+\[\.\][a-zA-Z0-9\-\.]+\[?\.\]?[a-zA-Z]{2,}\b`
- **Confidence**: High (85%+) when defanged
- **Characteristics**: Contains defanging markers like hxxp, [.], [dot]
- **Examples**:
  - `hxxps://evil[.]com/path`
  - `malicious[.]net`
  - `hxxp://phishing[.]com`

#### Full URLs
- **Pattern**: `\b(?:https?|ftp)://[^\s/$.?#].[^\s]*\b`
- **Confidence**: Medium-High (75-85%)
- **Characteristics**: Protocol + domain + optional path
- **Examples**:
  - `https://malicious.com/path/file.js`
  - `http://evil.net/payload`

### 3. Cryptocurrency IOCs

#### Bitcoin Address (Legacy P2PKH)
- **Pattern**: `\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b`
- **Confidence**: High (85%+)
- **Characteristics**: Starts with 1 or 3, 26-35 base58 characters
- **Examples**:
  - `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`
  - `3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy`

#### Bitcoin Address (Bech32)
- **Pattern**: `\bbc1[a-z0-9]{39,87}\b`
- **Confidence**: High (85%+)
- **Characteristics**: Starts with bc1, lowercase alphanumeric
- **Examples**:
  - `bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq`

#### Ethereum Address
- **Pattern**: `\b0x[a-fA-F0-9]{40}\b`
- **Confidence**: High (85%+)
- **Characteristics**: 0x prefix + 40 hex characters
- **Examples**:
  - `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`

### 4. Browser Extension IOCs

#### Chrome Extension ID
- **Pattern**: `\b[a-z]{32}\b`
- **Confidence**: Medium (60-70%)
- **Characteristics**: Exactly 32 lowercase letters
- **False Positives**: Random 32-char lowercase strings, MD5 hashes in lowercase
- **Context Required**: Should appear near "extension", "chrome", "addon"
- **Examples**:
  - `cjpalhdlnbpafiamejdnhcphjbkeiagm`
  - `nmmhkkegccagdldgiimedpiccmgmieda`

### 5. Email Addresses
- **Pattern**: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
- **Confidence**: Medium-High (75-85%)
- **Characteristics**: Standard email format
- **Context Required**: Distinguish malicious from legitimate
- **Examples**:
  - `phishing@evil.com`
  - `malware@attacker.net`

### 6. File Paths and Names

#### Windows File Path
- **Pattern**: `\b[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*\b`
- **Confidence**: Medium (70%)
- **Examples**:
  - `C:\Windows\System32\malware.exe`
  - `%APPDATA%\evil.dll`

#### Linux/Unix File Path
- **Pattern**: `\b/(?:[^/\0]+/)*[^/\0]+\b`
- **Confidence**: Low-Medium (50-60%)
- **False Positives**: URLs, dates
- **Examples**:
  - `/tmp/malware.sh`
  - `/var/log/suspicious.log`

## Confidence Scoring Strategy

### Very High Confidence (95-100%)
- **IOC Types**: MD5, SHA-1, SHA-256
- **Strategy**: Direct extraction, no LLM validation needed
- **Rationale**: Fixed length, hex-only, minimal false positives

### High Confidence (85-94%)
- **IOC Types**: IPv4, IPv6, Defanged URLs, Bitcoin addresses
- **Strategy**: Extract with regex, LLM validation only if context is ambiguous
- **Rationale**: Clear patterns but may need context validation

### Medium Confidence (70-84%)
- **IOC Types**: Domains, URLs, Email addresses
- **Strategy**: Regex extraction + LLM validation for threat relevance
- **Rationale**: Pattern matches but needs context to determine maliciousness

### Low Confidence (50-69%)
- **IOC Types**: Chrome extensions, File paths
- **Strategy**: Regex candidates + mandatory LLM validation
- **Rationale**: High false positive rate, context critical

## Context Clues for Validation

### Indicators of Malicious Context
- Proximity to keywords: "malicious", "C2", "C&C", "command and control", "exfiltration"
- Section headers: "IOCs", "Indicators", "Network Indicators", "File Hashes"
- Defanging markers: `[.]`, `hxxp`, `[dot]`, `[@]`
- Threat actor names, malware families nearby

### Indicators of Benign Context
- Documentation examples
- Code snippets (unless explicitly marked as malicious)
- Configuration examples
- Tutorial content

## Implementation Notes

### Regex Optimization
1. Use word boundaries (`\b`) to avoid partial matches
2. Compile patterns once and reuse
3. Use non-capturing groups `(?:...)` for performance
4. Consider case-insensitive flags where appropriate

### Deduplication Strategy
1. Normalize before deduplication (lowercase, remove defanging)
2. Track original and normalized forms
3. Preserve defanging in output for analyst review

### Performance Considerations
- Regex extraction: ~10-50ms per document
- LLM validation: ~500-2000ms per batch
- Target: 80%+ IOCs extracted via regex alone
- Expected cost reduction: 60-80% in LLM API calls