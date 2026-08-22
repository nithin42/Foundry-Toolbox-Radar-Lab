"""Unit and integration tests for foundry-toolbox-radar-lab (radar.py)."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from tool.radar import (
    Finding,
    Severity,
    audit_toolbox_config,
    check_missing_audience_user_entra_token,
    check_missing_auth_type,
    check_mutating_without_approval,
    check_overly_broad_scope,
    check_pii_and_secret_leakage,
    check_static_credential_risk,
    is_approval_enabled,
    main,
    normalize_auth_type,
    scan_for_pii_and_secrets,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CLEAN_FIXTURE = FIXTURES_DIR / "clean_toolbox.yaml"
RISKY_FIXTURE = FIXTURES_DIR / "risky_toolbox.yaml"


class TestNormalizationHelpers:
    """Tests for auth type normalization and approval helpers."""

    def test_normalize_auth_type(self) -> None:
        assert normalize_auth_type("CustomKeys") == "customkeys"
        assert normalize_auth_type("custom-keys") == "customkeys"
        assert normalize_auth_type("UserEntraToken") == "userentratoken"
        assert normalize_auth_type("user_entra_token") == "userentratoken"
        assert normalize_auth_type("AgenticIdentityToken") == "agenticidentitytoken"
        assert normalize_auth_type("OAuth2") == "oauth2"
        assert normalize_auth_type("None") is None
        assert normalize_auth_type(None) is None
        assert normalize_auth_type("") is None

    def test_is_approval_enabled(self) -> None:
        assert is_approval_enabled(True) is True
        assert is_approval_enabled(False) is False
        assert is_approval_enabled("true") is True
        assert is_approval_enabled("True") is True
        assert is_approval_enabled("always") is True
        assert is_approval_enabled("required") is True
        assert is_approval_enabled("never") is False
        assert is_approval_enabled("false") is False
        assert is_approval_enabled(None) is False


class TestRule01MutatingWithoutApproval:
    """RULE-01: Mutating verbs without require_approval gate (HIGH)."""

    def test_flagged_on_mutating_verb_without_approval(self) -> None:
        tool = {
            "name": "delete_customer_account",
            "description": "Remove customer records from database",
            "require_approval": False,
        }
        finding = check_mutating_without_approval(tool)
        assert finding is not None
        assert finding.rule_id == "RULE-01"
        assert finding.severity == Severity.HIGH

    def test_passed_when_require_approval_is_true(self) -> None:
        tool = {
            "name": "delete_customer_account",
            "description": "Remove customer records from database",
            "require_approval": True,
        }
        finding = check_mutating_without_approval(tool)
        assert finding is None

    def test_passed_for_read_only_tool(self) -> None:
        tool = {
            "name": "read_user_profile",
            "description": "Fetch user display name and email address",
            "require_approval": False,
        }
        finding = check_mutating_without_approval(tool)
        assert finding is None


class TestRule02MissingAuthType:
    """RULE-02: Missing or null authType (HIGH)."""

    def test_flagged_when_auth_type_missing(self) -> None:
        tool = {"name": "unauthenticated_tool", "target": "https://api.example.com"}
        finding = check_missing_auth_type(tool)
        assert finding is not None
        assert finding.rule_id == "RULE-02"
        assert finding.severity == Severity.HIGH

    def test_flagged_when_auth_type_is_none(self) -> None:
        tool = {"name": "unauthenticated_tool", "authType": "None"}
        finding = check_missing_auth_type(tool)
        assert finding is not None
        assert finding.rule_id == "RULE-02"
        assert finding.severity == Severity.HIGH

    def test_passed_when_valid_auth_type_present(self) -> None:
        tool = {"name": "secure_tool", "authType": "AgenticIdentityToken"}
        assert check_missing_auth_type(tool) is None


class TestRule03StaticCredentialRisk:
    """RULE-03: CustomKeys static credentials (MEDIUM)."""

    def test_flagged_for_custom_keys(self) -> None:
        tool = {"name": "legacy_service", "authType": "CustomKeys"}
        finding = check_static_credential_risk(tool)
        assert finding is not None
        assert finding.rule_id == "RULE-03"
        assert finding.severity == Severity.MEDIUM

    def test_passed_for_entra_or_oauth(self) -> None:
        assert check_static_credential_risk({"name": "t1", "authType": "UserEntraToken"}) is None
        assert check_static_credential_risk({"name": "t2", "authType": "AgenticIdentityToken"}) is None
        assert check_static_credential_risk({"name": "t3", "authType": "OAuth2"}) is None


class TestRule04MissingAudienceUserEntraToken:
    """RULE-04: UserEntraToken missing audience App ID URI (MEDIUM)."""

    def test_flagged_when_audience_missing(self) -> None:
        tool = {"name": "user_tool", "authType": "UserEntraToken"}
        finding = check_missing_audience_user_entra_token(tool)
        assert finding is not None
        assert finding.rule_id == "RULE-04"
        assert finding.severity == Severity.MEDIUM

    def test_passed_when_audience_specified(self) -> None:
        tool = {
            "name": "user_tool",
            "authType": "UserEntraToken",
            "audience": "api://contoso-api",
        }
        assert check_missing_audience_user_entra_token(tool) is None

    def test_ignored_for_other_auth_types(self) -> None:
        tool = {"name": "agent_tool", "authType": "AgenticIdentityToken"}
        assert check_missing_audience_user_entra_token(tool) is None


class TestRule05PIIAndSecretLeakage:
    """RULE-05: PII and secret leakage scanner."""

    def test_detects_email_and_phone(self) -> None:
        text = "Contact john.doe@example.com or call 555-432-1234."
        matches = scan_for_pii_and_secrets(text)
        categories = [cat for cat, _ in matches]
        assert "Email Address" in categories
        assert "Phone Number" in categories

    def test_detects_ssn(self) -> None:
        text = "SSN: 123-45-6789"
        matches = scan_for_pii_and_secrets(text)
        categories = [cat for cat, _ in matches]
        assert "SSN Pattern" in categories

    def test_detects_api_key_and_github_token(self) -> None:
        text = "sk-1234567890123456789012345 and ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
        matches = scan_for_pii_and_secrets(text)
        categories = [cat for cat, _ in matches]
        assert "AI API Key" in categories
        assert "GitHub Token" in categories

    def test_sample_output_produces_high_severity(self) -> None:
        tool = {
            "name": "leaky_tool",
            "sample_output": {"secret": "sk-1234567890123456789012345"},
        }
        findings = check_pii_and_secret_leakage(tool)
        assert len(findings) >= 1
        assert findings[0].severity == Severity.HIGH

    def test_description_produces_medium_severity(self) -> None:
        tool = {
            "name": "info_tool",
            "description": "Send alerts to devops@company.com",
        }
        findings = check_pii_and_secret_leakage(tool)
        assert len(findings) >= 1
        assert findings[0].severity == Severity.MEDIUM


class TestRule06OverlyBroadScope:
    """RULE-06: Wildcard and .default scopes (LOW)."""

    def test_flagged_for_wildcard_audience(self) -> None:
        tool = {"name": "broad_tool", "audience": "api://*"}
        finding = check_overly_broad_scope(tool)
        assert finding is not None
        assert finding.rule_id == "RULE-06"
        assert finding.severity == Severity.LOW

    def test_flagged_for_default_scope(self) -> None:
        tool = {"name": "broad_tool", "target": "https://management.azure.com/.default"}
        finding = check_overly_broad_scope(tool)
        assert finding is not None
        assert finding.rule_id == "RULE-06"
        assert finding.severity == Severity.LOW


class TestEndToEndFixtures:
    """End-to-end tests validating the fixture files."""

    def test_clean_toolbox_passes_all_checks(self) -> None:
        findings = audit_toolbox_config(CLEAN_FIXTURE)
        assert len(findings) == 0

    def test_risky_toolbox_triggers_all_rules(self) -> None:
        findings = audit_toolbox_config(RISKY_FIXTURE)
        assert len(findings) >= 6

        rule_ids = {f.rule_id for f in findings}
        expected_rules = {
            "RULE-01",
            "RULE-02",
            "RULE-03",
            "RULE-04",
            "RULE-05",
            "RULE-06",
        }
        assert expected_rules.issubset(rule_ids), f"Missing rules: {expected_rules - rule_ids}"

        severities = {f.severity for f in findings}
        assert Severity.HIGH in severities
        assert Severity.MEDIUM in severities
        assert Severity.LOW in severities


class TestCLIExecution:
    """Integration tests for the CLI runner (main)."""

    def test_cli_clean_fixture_exits_zero(self, capsys: pytest.CaptureFixture[str]) -> None:
        exit_code = main([str(CLEAN_FIXTURE)])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "[PASS]" in captured.out

    def test_cli_risky_fixture_exits_one(self, capsys: pytest.CaptureFixture[str]) -> None:
        exit_code = main([str(RISKY_FIXTURE)])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "[FAILED]" in captured.out
        assert "RULE-01" in captured.out

    def test_cli_json_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        exit_code = main([str(RISKY_FIXTURE), "--json"])
        assert exit_code == 1
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["passed"] is False
        assert data["high"] >= 2
        assert len(data["findings"]) >= 6

    def test_cli_missing_file_error(self, capsys: pytest.CaptureFixture[str]) -> None:
        exit_code = main(["non_existent_file.yaml"])
        assert exit_code == 2
