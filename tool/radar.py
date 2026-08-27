#!/usr/bin/env python3
"""Foundry Toolbox Radar (`radar.py`).

Open-source governance and risk scanner for Microsoft Foundry Toolbox configurations.
Audits tool definitions and connections for authorization creep, missing human-in-the-loop
approval policies, static credential usage, prompt injection attacks, and PII/secret data leakage before deployment.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from enum import Enum
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple
import yaml


class Severity(str, Enum):
    """Risk severity tiers for governance findings."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def __lt__(self, other: Severity) -> bool:
        order = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2}
        return order[self] < order[other]


@dataclass
class Finding:
    """Represents a governance scan finding."""

    rule_id: str
    rule_name: str
    severity: Severity
    tool_name: str
    message: str
    remediation: str
    field_name: Optional[str] = None
    snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding into a serializable dictionary."""
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


# ASSUMPTION: Mutating actions that should require human approval before execution.
# Grounded in Microsoft Learn Agent Service approval policy patterns.
MUTATING_VERBS_PATTERN = re.compile(
    r"\b(?:create|delete|update|send|write|modify|drop|remove|execute|post|patch|insert|destroy|exec|run_command|kill)\b",
    re.IGNORECASE,
)

# Supported auth types per Microsoft Learn:
# https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox
# CustomKeys, OAuth2, AgenticIdentityToken, UserEntraToken, None
SUPPORTED_AUTH_TYPES = {
    "customkeys",
    "oauth2",
    "agenticidentitytoken",
    "userentratoken",
    "none",
}

# Regex patterns for detecting PII and secrets
PII_EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
)
PII_PHONE_PATTERN = re.compile(
    r"\b(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?[2-9]\d{2}[-.\s]?\d{4}\b"
)
PII_SSN_PATTERN = re.compile(
    r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"
)
SECRET_GENERIC_KEY_PATTERN = re.compile(
    r"(?i)\b(?:api[_-]?key|secret[_-]?key|client[_-]?secret|password|access[_-]?token)\s*[:=]\s*['\"]?([A-Za-z0-9+/=_\-]{16,})['\"]?"
)
SECRET_AI_KEY_PATTERN = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{20,}|anthropic-[A-Za-z0-9_-]{20,})\b"
)
SECRET_GITHUB_TOKEN_PATTERN = re.compile(
    r"\b(?:ghp_[A-Za-z0-9]{30,40}|github_pat_[A-Za-z0-9_]{40,}|gho_[A-Za-z0-9]{30,40})\b"
)
SECRET_JWT_OR_BEARER_PATTERN = re.compile(
    r"\bBearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+\b",
    re.IGNORECASE,
)
SECRET_AZURE_CONN_STRING_PATTERN = re.compile(
    r"\b(?:DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+|Endpoint=sb://[^;]+;SharedAccessKeyName=[^;]+;SharedAccessKey=[^;]+)\b",
    re.IGNORECASE,
)
SECRET_PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----"
)

# Overly broad scope patterns
BROAD_SCOPE_WILDCARD = re.compile(r"\*")
BROAD_SCOPE_DEFAULT = re.compile(r"/\.default\b", re.IGNORECASE)

# Prompt injection & tool poisoning patterns (OWASP LLM01: Indirect Prompt Injection)
PROMPT_INJECTION_PATTERNS = [
    (
        "Instruction Hijacking / Override",
        re.compile(
            r"(?i)\b(?:ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions|disregard\s+(?:all\s+)?(?:previous|prior|above)\s+instructions|override\s+system\s+prompt|new\s+system\s+prompt|forget\s+(?:all\s+)?(?:previous|prior)\s+rules)\b"
        ),
    ),
    (
        "Role Alteration / Jailbreak",
        re.compile(
            r"(?i)\b(?:you\s+are\s+now\s+(?:an?\s+)?(?:unrestricted|developer\s+mode|dan|jailbreak|evil|god\s+mode)|act\s+as\s+an?\s+unrestricted\s+ai|bypass\s+(?:safety|security)\s+filters?)\b"
        ),
    ),
    (
        "Data Exfiltration Directive",
        re.compile(
            r"(?i)\b(?:exfiltrate\s+(?:data|tokens?|keys?|secrets?)|send\s+(?:all\s+)?(?:conversations?|user\s+data|secrets?|tokens?)\s+to\s+https?://|curl\s+-[A-Za-z]*X?\s*POST\s+https?://|fetch\s*\(\s*['\"]https?://[^'\"]+\?(?:token|secret|data)=)\b"
        ),
    ),
    (
        "Prompt Leaking Directive",
        re.compile(
            r"(?i)\b(?:repeat\s+(?:all\s+)?(?:words\s+)?above|print\s+(?:the\s+)?system\s+prompt|reveal\s+(?:your\s+)?instructions|output\s+initial\s+prompt)\b"
        ),
    ),
]


def normalize_auth_type(val: Any) -> Optional[str]:
    """Normalize authType string for uniform evaluation."""
    if val is None:
        return None
    raw = str(val).strip()
    if not raw or raw.lower() in ("none", "null", "undefined"):
        return None
    # Normalize hyphens and underscores: e.g. custom-keys -> customkeys
    cleaned = raw.lower().replace("-", "").replace("_", "")
    return cleaned


def is_approval_enabled(val: Any) -> bool:
    """Check if approval requirement is enabled (True or 'always')."""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ("true", "always", "require", "required")
    return False


def scan_for_pii_and_secrets(text: str) -> List[Tuple[str, str]]:
    """Scan arbitrary text for PII patterns and secrets.

    Returns a list of (Category, Matched_Snippet).
    """
    matches: List[Tuple[str, str]] = []
    if not text or not isinstance(text, str):
        return matches

    if PII_EMAIL_PATTERN.search(text):
        for m in PII_EMAIL_PATTERN.finditer(text):
            matches.append(("Email Address", m.group(0)))

    if PII_PHONE_PATTERN.search(text):
        for m in PII_PHONE_PATTERN.finditer(text):
            matches.append(("Phone Number", m.group(0)))

    if PII_SSN_PATTERN.search(text):
        for m in PII_SSN_PATTERN.finditer(text):
            matches.append(("SSN Pattern", m.group(0)))

    if SECRET_AI_KEY_PATTERN.search(text):
        for m in SECRET_AI_KEY_PATTERN.finditer(text):
            matches.append(("AI API Key", m.group(0)[:8] + "..."))

    if SECRET_GITHUB_TOKEN_PATTERN.search(text):
        for m in SECRET_GITHUB_TOKEN_PATTERN.finditer(text):
            matches.append(("GitHub Token", m.group(0)[:8] + "..."))

    if SECRET_JWT_OR_BEARER_PATTERN.search(text):
        matches.append(("Bearer JWT Token", "Bearer [REDACTED_JWT]"))

    if SECRET_AZURE_CONN_STRING_PATTERN.search(text):
        matches.append(("Azure Connection String", "DefaultEndpointsProtocol=https;..."))

    if SECRET_PRIVATE_KEY_PATTERN.search(text):
        matches.append(("Private Key Block", "-----BEGIN PRIVATE KEY-----"))

    if SECRET_GENERIC_KEY_PATTERN.search(text):
        for m in SECRET_GENERIC_KEY_PATTERN.finditer(text):
            matches.append(("Credential Key/Secret", m.group(0)[:12] + "..."))

    return matches


def check_mutating_without_approval(tool: Dict[str, Any]) -> Optional[Finding]:
    """RULE-01: Flag mutating tools without require_approval gate (HIGH)."""
    name = str(tool.get("name", ""))
    description = str(tool.get("description", ""))
    combined = f"{name} {description}"

    if MUTATING_VERBS_PATTERN.search(combined):
        approval_val = tool.get("require_approval")
        if not is_approval_enabled(approval_val):
            return Finding(
                rule_id="RULE-01",
                rule_name="MUTATING_WITHOUT_APPROVAL",
                severity=Severity.HIGH,
                tool_name=name or "<unnamed_tool>",
                message=(
                    f"Tool appears to perform mutating actions but does not enforce "
                    f"human approval (require_approval={approval_val!r})."
                ),
                remediation="Set 'require_approval: true' (or 'always') on mutating tools to prevent unauthorized autonomous actions.",
                field_name="require_approval",
                snippet=f"name: {name}, require_approval: {approval_val}",
            )
    return None


def check_missing_auth_type(tool: Dict[str, Any]) -> Optional[Finding]:
    """RULE-02: Flag connection without any authType or with an unrecognized authType (HIGH)."""
    name = str(tool.get("name", ""))
    raw_auth = tool.get("authType")
    norm_auth = normalize_auth_type(raw_auth)

    if norm_auth is None:
        return Finding(
            rule_id="RULE-02",
            rule_name="MISSING_AUTH_TYPE",
            severity=Severity.HIGH,
            tool_name=name or "<unnamed_tool>",
            message="No authentication type configured for tool/connection. Endpoints may be exposed unauthenticated.",
            remediation="Specify a supported 'authType' ('UserEntraToken', 'AgenticIdentityToken', 'OAuth2', or 'CustomKeys').",
            field_name="authType",
            snippet=f"authType: {raw_auth!r}",
        )

    if norm_auth not in SUPPORTED_AUTH_TYPES:
        return Finding(
            rule_id="RULE-02",
            rule_name="INVALID_AUTH_TYPE",
            severity=Severity.HIGH,
            tool_name=name or "<unnamed_tool>",
            message=f"Unrecognized authentication type '{raw_auth}'. Not a valid Microsoft Foundry authType.",
            remediation="Use one of the supported Foundry auth types: 'UserEntraToken', 'AgenticIdentityToken', 'OAuth2', or 'CustomKeys'.",
            field_name="authType",
            snippet=f"authType: {raw_auth!r}",
        )

    return None


def check_static_credential_risk(tool: Dict[str, Any]) -> Optional[Finding]:
    """RULE-03: Flag CustomKeys static credentials vs Entra token auth (MEDIUM)."""
    name = str(tool.get("name", ""))
    raw_auth = tool.get("authType")
    norm_auth = normalize_auth_type(raw_auth)

    if norm_auth == "customkeys":
        return Finding(
            rule_id="RULE-03",
            rule_name="STATIC_CREDENTIAL_RISK",
            severity=Severity.MEDIUM,
            tool_name=name or "<unnamed_tool>",
            message=(
                "Tool uses static 'CustomKeys' authentication (API key/PAT). "
                "Shared keys lack user attribution and automatic credential rotation."
            ),
            remediation="Upgrade connection to Microsoft Entra identity ('AgenticIdentityToken' or 'UserEntraToken') or 'OAuth2'.",
            field_name="authType",
            snippet=f"authType: {raw_auth}",
        )
    return None


# ASSUMPTION / TODO: confirm oauth2 vs UserEntraToken audience requirement once docs stabilize.
# UserEntraToken specifically requires an audience App ID URI for Entra token exchange,
# whereas OAuth2 connection definitions currently require client-id / client-secret / scopes.
def check_missing_audience_user_entra_token(tool: Dict[str, Any]) -> Optional[Finding]:
    """RULE-04: Flag UserEntraToken missing target audience App ID URI (MEDIUM)."""
    name = str(tool.get("name", ""))
    raw_auth = tool.get("authType")
    norm_auth = normalize_auth_type(raw_auth)

    if norm_auth == "userentratoken":
        audience = tool.get("audience")
        if not audience or not str(audience).strip():
            return Finding(
                rule_id="RULE-04",
                rule_name="MISSING_AUDIENCE_USER_ENTRA_TOKEN",
                severity=Severity.MEDIUM,
                tool_name=name or "<unnamed_tool>",
                message="Tool uses 'UserEntraToken' passthrough but lacks a specific 'audience' App ID URI.",
                remediation="Define a valid Entra App ID URI or Resource ID in 'audience' to avoid token rejection or broad token exchange.",
                field_name="audience",
                snippet=f"authType: {raw_auth}, audience: {audience!r}",
            )
    return None


def check_pii_and_secret_leakage(tool: Dict[str, Any]) -> List[Finding]:
    """RULE-05: Flag PII or secret leakage in sample_output (HIGH) and description (MEDIUM)."""
    name = str(tool.get("name", ""))
    findings: List[Finding] = []

    # Check sample_output -> HIGH severity
    sample_output = tool.get("sample_output")
    if sample_output is not None:
        text = json.dumps(sample_output) if isinstance(sample_output, (dict, list)) else str(sample_output)
        matches = scan_for_pii_and_secrets(text)
        for category, snippet in matches:
            findings.append(
                Finding(
                    rule_id="RULE-05",
                    rule_name="PII_OR_SECRET_LEAKAGE",
                    severity=Severity.HIGH,
                    tool_name=name or "<unnamed_tool>",
                    message=f"Potential {category} detected in 'sample_output'. Risk of sensitive data exposure to LLM context.",
                    remediation="Sanitize or synthesize sample outputs. Replace real PII or secret values with placeholders.",
                    field_name="sample_output",
                    snippet=snippet,
                )
            )

    # Check description -> MEDIUM severity
    description = tool.get("description")
    if description and isinstance(description, str):
        matches = scan_for_pii_and_secrets(description)
        for category, snippet in matches:
            findings.append(
                Finding(
                    rule_id="RULE-05",
                    rule_name="PII_OR_SECRET_LEAKAGE",
                    severity=Severity.MEDIUM,
                    tool_name=name or "<unnamed_tool>",
                    message=f"Potential {category} detected in 'description'. Risk of credential or PII leakage in prompt context.",
                    remediation="Remove sensitive credentials or PII from tool descriptions.",
                    field_name="description",
                    snippet=snippet,
                )
            )

    return findings


def check_overly_broad_scope(tool: Dict[str, Any]) -> Optional[Finding]:
    """RULE-06: Flag wildcards or broad .default scopes (LOW)."""
    name = str(tool.get("name", ""))
    target = str(tool.get("target", ""))
    audience = str(tool.get("audience", ""))
    scopes = str(tool.get("scopes", ""))

    combined = f"{target} {audience} {scopes}"

    if BROAD_SCOPE_WILDCARD.search(combined):
        return Finding(
            rule_id="RULE-06",
            rule_name="OVERLY_BROAD_SCOPE",
            severity=Severity.LOW,
            tool_name=name or "<unnamed_tool>",
            message="Wildcard character '*' detected in target, audience, or scope definition.",
            remediation="Specify explicit resource identifiers and endpoints instead of wildcard patterns.",
            field_name="target/audience",
            snippet=combined.strip()[:60],
        )

    if BROAD_SCOPE_DEFAULT.search(combined):
        return Finding(
            rule_id="RULE-06",
            rule_name="OVERLY_BROAD_SCOPE",
            severity=Severity.LOW,
            tool_name=name or "<unnamed_tool>",
            message="Broad '.default' scope used. Consider scoping permissions to granular OAuth/Entra roles if supported.",
            remediation="Use least-privilege delegated scopes (e.g. 'Files.Read') where possible rather than full resource default.",
            field_name="audience/scopes",
            snippet=combined.strip()[:60],
        )

    return None


def check_prompt_injection_and_tool_poisoning(tool: Dict[str, Any]) -> List[Finding]:
    """RULE-07: Flag prompt injection or tool poisoning in description, name, or sample_output (HIGH)."""
    name = str(tool.get("name", ""))
    findings: List[Finding] = []

    fields_to_check: List[Tuple[str, str]] = [
        ("description", str(tool.get("description", ""))),
        ("name", name),
    ]

    sample_output = tool.get("sample_output")
    if sample_output is not None:
        text = json.dumps(sample_output) if isinstance(sample_output, (dict, list)) else str(sample_output)
        fields_to_check.append(("sample_output", text))

    for field_name, content in fields_to_check:
        if not content:
            continue
        for category, pattern in PROMPT_INJECTION_PATTERNS:
            m = pattern.search(content)
            if m:
                findings.append(
                    Finding(
                        rule_id="RULE-07",
                        rule_name="PROMPT_INJECTION_OR_TOOL_POISONING",
                        severity=Severity.HIGH,
                        tool_name=name or "<unnamed_tool>",
                        message=f"Potential {category} detected in '{field_name}'. Tool metadata attempts to hijack agent control flow or exfiltrate context.",
                        remediation="Remove instruction-override phrases, prompt injection attacks, and exfiltration directives from tool metadata.",
                        field_name=field_name,
                        snippet=m.group(0),
                    )
                )

    return findings


def extract_tools_from_config(config_data: Any) -> List[Dict[str, Any]]:
    """Extract tool entries from a loaded YAML configuration dictionary or list."""
    if isinstance(config_data, list):
        return [item for item in config_data if isinstance(item, dict)]

    if isinstance(config_data, dict):
        if "tools" in config_data and isinstance(config_data["tools"], list):
            return [t for t in config_data["tools"] if isinstance(t, dict)]
        if "connections" in config_data and isinstance(config_data["connections"], list):
            return [c for c in config_data["connections"] if isinstance(c, dict)]
        # Single tool definition object
        if "name" in config_data or "target" in config_data or "authType" in config_data:
            return [config_data]

    return []


def audit_toolbox_config(config_path: Path) -> List[Finding]:
    """Parse and scan a Toolbox YAML configuration file for governance findings."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    tools = extract_tools_from_config(data)
    findings: List[Finding] = []

    for tool in tools:
        # RULE-01
        f1 = check_mutating_without_approval(tool)
        if f1:
            findings.append(f1)

        # RULE-02
        f2 = check_missing_auth_type(tool)
        if f2:
            findings.append(f2)

        # RULE-03
        f3 = check_static_credential_risk(tool)
        if f3:
            findings.append(f3)

        # RULE-04
        f4 = check_missing_audience_user_entra_token(tool)
        if f4:
            findings.append(f4)

        # RULE-05
        findings.extend(check_pii_and_secret_leakage(tool))

        # RULE-06
        f6 = check_overly_broad_scope(tool)
        if f6:
            findings.append(f6)

        # RULE-07
        findings.extend(check_prompt_injection_and_tool_poisoning(tool))

    return findings


def format_table(findings: List[Finding], config_path: Path) -> str:
    """Format findings into a clean human-readable ASCII table."""
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append(f" FOUNDRY TOOLBOX RADAR - GOVERNANCE AUDIT REPORT")
    lines.append(f" Target File: {config_path.name}")
    lines.append("=" * 80)

    if not findings:
        lines.append("\n  [PASS] No governance or data-leakage risks detected.")
        lines.append("  Toolbox configuration complies with governance baseline.\n")
        lines.append("=" * 80)
        return "\n".join(lines)

    high_count = sum(1 for f in findings if f.severity == Severity.HIGH)
    med_count = sum(1 for f in findings if f.severity == Severity.MEDIUM)
    low_count = sum(1 for f in findings if f.severity == Severity.LOW)

    lines.append(f" Total Findings: {len(findings)} (HIGH: {high_count}, MEDIUM: {med_count}, LOW: {low_count})")
    lines.append("-" * 80)
    lines.append(f"{'SEVERITY':<10} | {'RULE ID':<9} | {'TOOL NAME':<18} | {'MESSAGE'}")
    lines.append("-" * 80)

    for f in findings:
        sev_badge = f"[{f.severity.value}]"
        tool_display = (f.tool_name[:16] + "..") if len(f.tool_name) > 18 else f.tool_name
        lines.append(f"{sev_badge:<10} | {f.rule_id:<9} | {tool_display:<18} | {f.message}")
        if f.snippet:
            lines.append(f"  --> Snippet:     {f.snippet}")
        lines.append(f"  --> Remediation: {f.remediation}")
        lines.append("-" * 80)

    lines.append("=" * 80)
    if high_count > 0:
        lines.append(f" [FAILED] {high_count} HIGH severity finding(s) detected. Gate blocked.")
    else:
        lines.append(f" [WARNING] Audit passed with {med_count} MEDIUM and {low_count} LOW warnings.")
    lines.append("=" * 80)

    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint for radar.py."""
    parser = argparse.ArgumentParser(
        prog="radar.py",
        description="Audit Microsoft Foundry Toolbox configurations for governance and data-leakage risks.",
    )
    parser.add_argument(
        "config",
        type=Path,
        nargs="?",
        default=None,
        help="Path to the Toolbox YAML configuration file to scan.",
    )
    parser.add_argument(
        "--config",
        dest="config_opt",
        type=Path,
        help="Optional named parameter for config path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output for CI/CD gates.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on MEDIUM warnings in addition to HIGH findings.",
    )

    args = parser.parse_args(argv)
    target_path: Optional[Path] = args.config_opt or args.config

    if not target_path:
        parser.print_help()
        return 2

    try:
        findings = audit_toolbox_config(target_path)
    except Exception as err:
        if args.json:
            print(json.dumps({"error": str(err), "file": str(target_path)}))
        else:
            print(f"Error reading configuration '{target_path}': {err}", file=sys.stderr)
        return 2

    if args.json:
        report = {
            "file": str(target_path),
            "total_findings": len(findings),
            "high": sum(1 for f in findings if f.severity == Severity.HIGH),
            "medium": sum(1 for f in findings if f.severity == Severity.MEDIUM),
            "low": sum(1 for f in findings if f.severity == Severity.LOW),
            "passed": not any(f.severity == Severity.HIGH for f in findings),
            "findings": [f.to_dict() for f in findings],
        }
        print(json.dumps(report, indent=2))
    else:
        print(format_table(findings, target_path))

    # Exit code determination
    has_high = any(f.severity == Severity.HIGH for f in findings)
    has_medium = any(f.severity == Severity.MEDIUM for f in findings)

    if has_high or (args.strict and has_medium):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
