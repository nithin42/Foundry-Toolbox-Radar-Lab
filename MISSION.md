# MISSION: foundry-toolbox-radar-lab

## 1. What we're building

`foundry-toolbox-radar-lab` — an open-source CLI tool (`radar.py`) that scans a Microsoft Foundry **Toolbox** configuration for governance and data-leakage risk *before* it's wired to an agent, plus a 3-part hands-on workshop that teaches people to use it. This is not a generic "connect an MCP tool" tutorial — the differentiator is the security/governance angle: catching under-governed tools (missing approval gates, over-broad auth scopes, PII/secrets leaking through tool descriptions or sample outputs) before they go live.

Audience: developers already building agents on Microsoft Foundry who want a practical governance check, not just a "how to connect MCP" walkthrough.

---

## 2. Non-negotiable constraints

- Python 3.10+, type hints on all public functions, docstrings on every module/function.
- MIT license.
- No external paid services required to run `radar.py` — it operates on a local config file, no live Azure call needed for the core scan.
- Docs must link to real Microsoft Learn URLs, never paraphrase-and-claim without linking.
- Repo structure is fixed.
- Tone in docs: direct, practical, first-person-plausible but never a fabricated personal anecdote.
