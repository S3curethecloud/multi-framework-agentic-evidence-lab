# Phase 2 - Mock SOC 2 Evidence Dataset

**Status:** Evidence Recorded
**Phase type:** Dataset baseline
**Runtime authority:** None
**Framework implementation:** None

## Goal

Create the local mock evidence dataset used by every framework implementation in later phases.

The dataset must support fair comparison across LangChain, LangGraph, Strands, and ADK by giving each implementation the same evidence surface, same gaps, and same retrieval target.

## Scope

Phase 2 adds mock files under:

```text
data/policies/
data/evidence/
data/logs/
data/tickets/
```

The dataset includes policy expectations, evidence records, system-style logs, and ticket-style context.

## Dataset files

### Policies

- `data/policies/access_control_policy.md`
- `data/policies/change_management_policy.md`
- `data/policies/incident_response_policy.md`

### Evidence

- `data/evidence/mfa_rollout_evidence.md`
- `data/evidence/privileged_access_review.md`
- `data/evidence/terminated_user_access_removal.md`
- `data/evidence/production_deploy_approval.md`

### Logs

- `data/logs/iam_sample_export.json`
- `data/logs/access_review_log.json`
- `data/logs/deployment_log.json`

### Tickets

- `data/tickets/jira_access_review_ticket.md`
- `data/tickets/change_approval_ticket.md`

## Intentional gaps

The dataset intentionally includes evidence gaps so agents can practice sufficiency scoring and human-review routing:

- missing privileged-access reviewer identity;
- missing approval timestamp;
- stale or incomplete access review closure;
- MFA conflict for break-glass and contractor accounts;
- missing contractor expiration date;
- incomplete terminated-user privileged group removal confirmation;
- unclear secondary approval requirement for a production deployment;
- incident response policy without tabletop exercise evidence.

## Boundary

This phase creates mock local files only.

It does not add framework implementation, live backend integration, token issuance, authorization behavior, runtime session creation, provider mutation, Kubernetes mutation, production deployment, production enforcement, SOC 2 certification, independent audit completion, or production operating-effectiveness evidence.

## Verification

Phase 2 verification checks:

- required dataset files exist;
- expected evidence identifiers are present;
- expected intentional gaps are present;
- the shared document loader can load dataset records;
- lexical retrieval can find access-control and change-management evidence;
- forbidden positive-claim scan passes;
- framework implementation files are still absent.

## Evidence

- Verification script: `tools/verify_phase_2.py`
- Verification printout: `docs/verification/PHASE_2_VERIFICATION_PRINTOUT.txt`
