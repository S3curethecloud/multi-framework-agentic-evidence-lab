# Agent Operating Instructions

## Required first-read

Before building or changing this repository, read the canonical SecureTheCloud doctrine control plane:

- `S3curethecloud/securethecloud-doctrine-control-plane`
- `AGENTS.md`
- `doctrine.lock.md`
- `docs/portfolio/AGENT_CONSUMPTION_GUIDE.md`
- `docs/portfolio/SUITE_CATALOG.md`
- `docs/portfolio/MODULE_AUTHORITY_MATRIX.md`
- `docs/portfolio/STATUS_TAXONOMY.md`
- `docs/portfolio/COMPOSITION_LAYER_DOCTRINE.md`
- `docs/portfolio/SENTINEL_CONTROL_POINT_RULE.md`
- `docs/portfolio/PRODUCT_PACKAGING_BOUNDARIES.md`
- `docs/soc2/*.md`
- `contracts/portfolio/*.json`

## Local repository purpose

This repository is a portfolio lab for agent-framework comparison. It does not define SecureTheCloud doctrine and must not create local substitute doctrine.

## Local authority boundary

This lab may implement local mock-data agent workflows for comparison only.

This lab must not claim or implement:

- SOC 2 certification;
- independent audit completion;
- production operating effectiveness;
- live enforcement;
- production authorization;
- token issuance;
- runtime session creation;
- provider mutation;
- Kubernetes mutation;
- production traffic cutover;
- SENTINEL bypass;
- credential or secret handling;
- live customer evidence mutation.

## Phase-gate rule

Each phase must produce a verification printout before the next phase begins.

The verification printout must include:

- current phase status;
- expected artifact check;
- forbidden-claim scan;
- consistency findings;
- open errors to fix before moving forward.
