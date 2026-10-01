# ADR-002: One self-contained skill per agent class; two class skills per agent

**Status:** accepted
**Date:** 2026-09-24
**Approved by:** Commander (the Commander's word)

## Context
The Commander's rule for the Parrot Protocol: "each skill stand alone ... I only need to load in one skill per agent per class". He also said: "Project Leader skills should be 2 skills total. [Both IT managers] get the ITM skills 2 skills total. all workers get worker skills 2 skills total." (Square brackets mark words replaced for this public copy.)

## Decision
Three skills here: `module-sop-project-leader`, `module-sop-itm`, `module-sop-worker`. Each agent installs its class's skill from this repo plus `parrot-protocol-<class>` from `parrot-protocol`. No agent needs anything else from either repo.

## Reasons
Separate repos keep separate owners and versions: the Parrot Protocol and this repo are each released on their own schedule.

## Consequences
- The class SOP and the MODULE SOP are duplicated in each skill's `references/`, by design.
- `verify_skills.py` keeps the copies identical.
