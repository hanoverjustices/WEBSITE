# Executed test results

`node scripts/build_gia.cjs && node gia/test.cjs`: PASS, 32 checks.

Covered: three Custos question variants including custous; historical answer/citation distinction; 17 unsupported questions including current officers, personal/legal details, other parishes, compound queries, injection and follow-ups; seven invalid evidence cases; contradictory records; missing sources; null publication dates; all eight topic categories; syntax of every inline script and removal of the old master answer switch.

`node gia/browser-test.cjs`: BLOCKED before browser launch. The installed Playwright package could not find its Chromium headless executable. No browser interaction, mobile layout or live deployment success is claimed.

Source audit: one approved historical record, nine unverified records. OPM source inspected; MOJ retrieval failed/timed out, King's House returned 403 and JIS article retrieval failed. These failed fetches did not approve new records.

No current legal, annual-report, JP eligibility, contact or HJPA officer answer is verified. These remain intentionally blocked. The technical gate cannot itself prove an editor's factual claim or detect every semantic contradiction. Continued human source review is required.
