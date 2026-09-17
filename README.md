# Gia source-locked rebuild

## Install

Upload ONLY the included index.html to the repository root, replacing index.html. Leave all folders, photos, CNAME and publishing workflow unchanged. This file embeds the reviewed records and engine: there are no extra runtime files to upload. This package does not deploy itself.

## What is approved

One historical record: the Office of the Prime Minister's account of Lennox Anderson-Jackson's installation ceremony on 17 July 2025, published 31 July 2025. It supports the historical event, not a claim of independently confirmed current officeholding.

## Audit on 16 September 2026

Leadership/current Custos, HJPA officers, JP services, becoming a JP, annual reports, resources, events, contacts and legal guidance are UNVERIFIED and blocked. Existing site text, officers arrays, scraped passages and uploaded posters are not automatically approved. MOJ retrieval timed out/failed; King's House returned 403; JIS article retrieval failed. Search snippets were not approved as evidence. No current legal or procedural answer has been approved.

This intentionally reduces coverage. Obtain an authorised dated HJPA roster and original approved event notices; obtain accessible official MOJ procedures, form provenance, contacts and current legislation before approving more answers. No owner confirmation was fabricated.

## Maintenance

The single knowledge-editing location is gia/knowledge.json. Each approved record needs a reviewed answer, sourceIds, exact question aliases, temporalStatus, effective dates where known, a factKey and value for conflict comparison. Each source needs publisher, title, HTTPS URL, section/page, supporting excerpt, separate publication/update and verification dates, reviewDue, status and applicable topic scope. Null publication/update dates display Not stated. Review dates are editorial review deadlines, not legal deadlines.

Official government sources rank 1 for responsible issuing authorities, 2 for other directly relevant official sources; authorised HJPA records rank 1 only within association topics. News is not approved by this engine. Rank orders citations, NEVER suppresses contradictions. Conflicts sharing factKey and overlapping periods block answers; undetected semantic conflicts remain a human review responsibility. Approved means human-reviewed, not machine proof of truth. Code validates metadata/provenance/freshness, not the truth of arbitrary text entered by an editor.

Run node scripts/build_gia.cjs then node gia/test.cjs before uploading the rebuilt index.html. Source audit can be typed into Gia. Unreviewed changes never become approved merely because a link works. Live link availability is not checked in the visitor's browser: the last reviewed snapshot is used until reviewDue. Later source removal may not be detected until another audit.

Queries are exact approved aliases after punctuation/case/spacing normalisation and two explicit Custos typo corrections. Unsupported wording refuses; add reviewed aliases as needed. This favours precision over conversational coverage. No model, unrestricted search, automatic poster OCR, inferred follow-up or general-knowledge fallback is used. No user messages are stored persistently or transmitted by this engine. Existing website functions outside Gia have not been audited or changed.

Legacy answer helper definitions remain inert for compatibility with site functions, but the sole chat answer entry point now calls the locked engine. Changing records requires developer/reviewer access, not a chat instruction.

## Verification limits

Tests cover the engine, evidence gates, current/historical distinction, role confusion, injection attempts, conflicts and inline script syntax. Visual browser interaction and live deployment have not been verified. No absolute-accuracy guarantee is made.
