# Governance Notes

## Scope

This repository is a mock-data learning and portfolio lab for comparing agent frameworks.

It is not a production SecureTheCloud module, not a doctrine source of truth, and not an evidence authority.

## Doctrine consumption

The lab follows the canonical SecureTheCloud doctrine control-plane boundary model. Human-readable doctrine and machine-readable contracts in the doctrine control-plane repository remain the authority for SecureTheCloud suite, module, packaging, status, and authority claims.

This repository must not create local substitute doctrine.

## SOC 2 wording boundary

This lab may use SOC 2-style mock evidence for controlled agent evaluation.

It must not claim:

- SOC 2 certification;
- independent SOC 2 audit completion;
- Type 1 or Type 2 attestation;
- production operating effectiveness;
- auditor attestation;
- live control operation.

## Runtime boundary

This repository does not implement production runtime behavior.

No phase may add production deployment, live backend integration, authorization behavior, token issuance, runtime session creation, provider mutation, Kubernetes mutation, production enforcement, or SENTINEL bypass.

## Evidence boundary

All evidence in `data/` is mock evidence unless explicitly marked otherwise.

The agent may evaluate mock evidence sufficiency for lab purposes only. The agent must not present mock evidence as real customer, production, or audit evidence.

## Human-review boundary

Human review in this lab is simulated unless a future phase explicitly defines a local-only reviewer input mechanism.

Human-review routing is a workflow comparison feature. It is not an approval of real controls or real evidence.
