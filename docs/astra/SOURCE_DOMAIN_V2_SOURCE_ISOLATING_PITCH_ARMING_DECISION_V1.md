# Astra V2 source-isolating pitch diagnostic arming decision V1

Date: 2026-09-28
Status: **GO — ONE SYNTHETIC/MODEL-FREE DIAGNOSTIC ATTEMPT**

Launch identity:
`source-domain-v2-isolated-pitch-20260928-canonical-01`

Basis:
- package statically verified;
- exact frozen Stage-A sample and hashes preserved;
- no model or real-data access;
- user instructed continuation at discretion until explicit authorization is required.

One-shot rules:
- one workflow run only;
- no automatic retry;
- exact control/manifest/failed-Stage-A hashes pinned;
- max 172 probe renders / 344 synthetic seconds;
- no Stage-A rerun;
- no Stage B/model work in this workflow;
- P1/P2/P3 false;
- freeze pass/failure afterward.
