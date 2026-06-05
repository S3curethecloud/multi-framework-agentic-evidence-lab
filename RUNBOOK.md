# Runbook

## Phase workflow

Use this sequence for every phase:

1. Read the current phase file in `docs/phases/`.
2. Implement only the scoped artifacts for that phase.
3. Run the phase verification script.
4. Review the verification printout.
5. Fix all blocking errors.
6. Record phase evidence.
7. Move to the next phase only after verification is clean.

## Phase 0 verification

```bash
python tools/verify_phase_0.py
```

Expected outcome:

- all required baseline files exist;
- forbidden claims are absent;
- required directories exist;
- phase tracker is present;
- verification summary is printed.

## Local development assumptions

Phase 0 adds no external dependencies.

Later phases may add Python dependencies only after the shared foundation is defined.

## Git hygiene

Recommended commit sequence:

```text
01. Initialize lab baseline and governance boundary
02. Add shared foundation schemas and trace envelope
03. Add mock SOC 2 evidence dataset
04. Implement LangChain baseline RAG agent
05. Implement LangGraph governed workflow
06. Implement Strands implementation
07. Implement ADK implementation
08. Add comparison matrix and executive summary
```
