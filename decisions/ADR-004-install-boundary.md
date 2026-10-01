# ADR-004: Install boundary

**Status:** accepted, amended 2026-09-30 (the repository is published as a clean release; the install boundary is unchanged)
**Date:** 2026-09-24
**Approved by:** Commander (WO-001)

## Context
Skills are installed per agent: Claude Code and Hermes folders, locking (read-only, `chattr +i`, Hermes curator pin) and always-on lines (CLAUDE.md / SOUL.md). All of that depends on paths and hosts specific to each deployment.

## Decision
- This repo produces and verifies the skills only.
- Install tooling lives outside this repo, with each deployment's own operations.
- An installer copies only `SKILL.md` + `references/`, into a folder named after the skill.

## Reasons
Keeps deployment specifics (hosts, paths, agent names beyond the class list) out of the SOP source, and keeps the install boundary simple.

## Consequences
The installer must verify installed files against this repo's commit (sha256) from each agent's own side.

## Amendment (2026-09-30)
This ADR's former claim that the repository would never reach a public mirror is dropped; the install-boundary decision itself is unchanged.
