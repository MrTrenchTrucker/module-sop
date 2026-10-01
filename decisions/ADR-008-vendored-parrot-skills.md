# ADR-008: The Parrot Protocol class skills are vendored here, byte-for-byte, pinned to their source commit

**Status:** accepted
**Date:** 2026-09-24
**Approved by:** Commander (2026-09-24 ~19:4xZ): "The repo has clean release skills so they can stand alone and reference what they need to like parrot protocol which we can also add to that repo as well since [the IT manager] finished the Parrot Protocol repo. Parrot protocol repo looks clean." (Square brackets mark words replaced for this public copy.)

## Context
Each agent carries two class skills: its MODULE SOP skill and its Parrot Protocol skill. The Parrot Protocol has its own repository, `parrot-protocol` (v0.2.0, merged after a non-author gate). It is headed for public release, so it stays separate (ADR-002).

## Decision
- Each class pack here carries both skills: `skills/<class>/module-sop-<class>/SKILL.md` (authored here) and `skills/<class>/parrot-protocol-<class>/SKILL.md` (vendored).
- The vendored copies are **byte-for-byte** copies of the source repo's `skills/<class>/SKILL.md` at the commit recorded in `skills/PARROT_PIN.toml`, with each file's sha256.
- A test fails if any vendored file's sha256 drifts from the pin.

## Reasons
- One place to install every agent's skills from, while the Parrot Protocol keeps a single canonical source.
- A vendored copy is never edited here: an edit would silently fork the protocol.

## Consequences
- Updating the Parrot skills means: bump the pin to a new source commit, copy the files, update the checksums, and commit on the Commander's word.
- Fixes to the Parrot text go to the Parrot repo, never here.
