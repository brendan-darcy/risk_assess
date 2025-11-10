# VSCode Extension Security Audit Tools

## Overview

Two security audit scripts for analyzing VSCode extensions:

1. **vscode_extension_audit.py** - Basic security checks
2. **vscode_extension_audit_enhanced.py** - Comprehensive analysis with Marketplace API

## Quick Start

```bash
# Basic audit
python3 security-tools/vscode_extension_audit.py

# Enhanced audit (recommended)
python3 security-tools/vscode_extension_audit_enhanced.py
```

## Enhanced Script Features

### 1. Marketplace API Integration

Checks each extension against the VS Code Marketplace:
- **Rating & Reviews**: Average rating and number of reviews
- **Install Count**: Total installations (popularity indicator)
- **Publisher Verification**: Whether publisher is verified by Microsoft
- **Last Updated**: When extension was last updated

**Why it matters:** Popular, well-rated extensions from verified publishers are generally safer.

### 2. Threat Scoring System

Calculates a risk score (0-100+) based on:

| Factor | Points | What It Means |
|--------|--------|---------------|
| Known malicious | +100 | In threat database |
| Suspicious name | +20 | Contains 'hack', 'crack', etc. |
| Numeric publisher | +30 | Publisher name is all numbers |
| Short publisher name | +20 | Less than 3 characters |
| Low installs (<100) | +15 | Very unpopular |
| Poor rating (<2.0) | +25 | Users rate it badly |
| Unverified publisher | +10 | Not verified by Microsoft |
| Can't verify | +5 | Not found on marketplace |
| Activates on startup | +15 | Runs automatically |

**Risk Levels:**
- **HIGH** (50+): Immediate review needed
- **MEDIUM** (25-49): Investigate carefully
- **LOW** (10-24): Minor concerns
- **MINIMAL** (<10): Appears safe

### 3. Permission Analysis

Reads `package.json` to identify:
- **Activation Events**: When extension starts running
- **Contributed Features**: Commands, views, languages it adds
- **Execution Scripts**: Build/install scripts
- **File System Access**: Can it read/write files

**High-risk permissions:**
- File system access (`workspace.fs`)
- Environment variables (`env.`)
- Command execution
- Webview creation (can run JavaScript)

### 4. Known Threat Database

Maintains list of known malicious extensions:
- Malware signatures
- Compromised extensions
- Suspicious patterns

Currently basic - can be expanded with threat intelligence feeds.

## Your Results Explained

### ⚠️ Medium Risk Findings

**ms-python.vscode-python-envs (Rating: 1.4/5)**
- ✅ From Microsoft (verified publisher)
- ⚠️ Poor user ratings
- **Verdict:** Likely not malicious, just buggy/unpopular
- **Action:** Safe to keep if you use it, but monitor

**reditorsupport.r-syntax (Rating: 1.0/5)**
- ⚠️ Unverified publisher
- ⚠️ Very poor rating
- **Verdict:** Low install count, might be abandoned
- **Action:** Consider removing if you don't use R

### ✅ Safe Extensions (21)

All from verified publishers:
- Microsoft (ms-python, ms-toolsai, ms-vscode)
- GitHub (github.copilot, github.remotehub)
- Anthropic (claude-code)
- RedHat (vscode-yaml)
- Postman

**Total installs:** 1+ billion across all your extensions
**Average rating:** 3.59/5

## Interpreting Scores

### Your Extensions' Threat Scores

| Score Range | Count | Risk Level | Action Required |
|-------------|-------|------------|-----------------|
| 50+ | 0 | HIGH | Immediate review |
| 25-49 | 2 | MEDIUM | Investigate |
| 10-24 | 0 | LOW | Monitor |
| <10 | 21 | MINIMAL | Safe |

**Key Insight:** Your extension ecosystem is very safe. The two flagged extensions are from legitimate sources but have poor ratings, not security issues.

## Advanced Usage

### View Detailed JSON Report

```bash
cat /tmp/vscode_security_audit.json | python3 -m json.tool
```

### Filter High-Risk Extensions

```bash
python3 security-tools/vscode_extension_audit_enhanced.py | grep "HIGH RISK" -A 20
```

### Check Specific Extension

```python
from vscode_extension_audit_enhanced import ExtensionAnalyzer

analyzer = ExtensionAnalyzer()
data = analyzer.check_marketplace("ms-python.python")
print(data)
```

## Threat Database Updates

To add known malicious extensions, edit the script:

```python
KNOWN_THREATS = {
    "malicious.extension": "Steals credentials",
    "fake.publisher": "Impersonates legitimate extension"
}
```

Sources for threat intelligence:
- [VSCode Security Advisories](https://code.visualstudio.com/blogs/)
- [GitHub Security Lab](https://securitylab.github.com/)
- [OSSF Malicious Packages](https://github.com/ossf/malicious-packages)

## Security Best Practices

### Before Installing Extensions

1. **Check publisher** - Is it verified? Recognizable?
2. **Read reviews** - What are users saying?
3. **Check install count** - Is it popular?
4. **Review permissions** - What does it need access to?
5. **Check source code** - Is it open source?

### Regular Audits

Run this audit:
- **Monthly** - Check for new installs
- **After updates** - Verify extension behavior hasn't changed
- **Before sensitive work** - Ensure clean environment

### Red Flags to Watch For

❌ **Never install extensions that:**
- Have numeric/random publisher names
- Request excessive permissions
- Have <100 installs and no reviews
- Contain "crack", "nulled", "keygen" in name
- Are from unverified publishers for sensitive tasks

## Comparison: Basic vs Enhanced

| Feature | Basic | Enhanced |
|---------|-------|----------|
| List extensions | ✅ | ✅ |
| Check publisher names | ✅ | ✅ |
| Keyword matching | ✅ | ✅ |
| Marketplace ratings | ❌ | ✅ |
| Install counts | ❌ | ✅ |
| Publisher verification | ❌ | ✅ |
| Threat scoring | ❌ | ✅ |
| Permission analysis | ❌ | ✅ |
| Known threats | ❌ | ✅ |
| JSON report | ❌ | ✅ |

## Limitations

**What these scripts DON'T detect:**
- Zero-day malware
- Obfuscated malicious code
- Time-bomb trojans
- Supply chain attacks
- Network-based threats
- Runtime behavior

**For comprehensive security:**
- Use alongside antivirus
- Monitor network activity
- Review extension updates
- Follow least privilege principle

## Troubleshooting

### "No extensions found"

```bash
# Check VSCode is installed
ls "/Applications/Visual Studio Code.app"

# Check extensions directory
ls -la ~/.vscode/extensions

# Install 'code' command
# VSCode → Command Palette → "Shell Command: Install 'code' command in PATH"
```

### Marketplace API errors

The script gracefully handles API failures. Extensions will show as "Could not verify on marketplace" with a small score penalty.

### Timeout issues

Increase timeout in script:
```python
response = requests.post(url, json=payload, headers=headers, timeout=10)  # Increase from 5
```

## Contributing

To improve the threat database:
1. Research known malicious VSCode extensions
2. Add to `KNOWN_THREATS` dictionary
3. Document the threat source
4. Submit update

## References

- [VSCode Extension Security](https://code.visualstudio.com/api/references/extension-manifest)
- [Marketplace API](https://marketplace.visualstudio.com/api)
- [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)

## Files

```
security-tools/
├── vscode_extension_audit.py              # Basic audit
├── vscode_extension_audit.sh              # Bash version (basic)
├── vscode_extension_audit_enhanced.py     # Enhanced audit
└── EXTENSION_AUDIT_README.md              # This file
```

## Quick Reference

```bash
# Run enhanced audit
python3 security-tools/vscode_extension_audit_enhanced.py

# Save output to file
python3 security-tools/vscode_extension_audit_enhanced.py > audit_$(date +%Y%m%d).txt

# View detailed JSON
cat /tmp/vscode_security_audit.json | jq

# Check specific metric
cat /tmp/vscode_security_audit.json | jq '.[].marketplace.rating' | sort -n
```
