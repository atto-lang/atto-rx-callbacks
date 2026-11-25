> **AI agent instructions (organization-wide):** Before working on code, issues, or pull requests, read and follow the [organization `AGENTS.md`](https://github.com/atto-lang/.github/blob/main/AGENTS.md), including its **merge-first stealth-development policy**. Honor any repository-local `AGENTS.md`, explicit holds, and GitHub-enforced rules.

# atto-rx-callbacks

Callback interoperability and reactive event abstractions for AttoLang.

## Naming migration and language authority

This repository is maintained at [atto-lang/atto-rx-callbacks](https://github.com/atto-lang/atto-rx-callbacks); use `https://github.com/atto-lang/atto-rx-callbacks.git` for Git remotes and canonical `.atto` source examples. The normative language contract is [atto-spec](https://github.com/atto-lang/atto-spec), with executable guest evidence tracked by [atto-platform-conformance](https://github.com/atto-lang/atto-platform-conformance). Follow current ownership, borrowing, effects, actor, and syntax rules there; do not infer implemented features from a README or unexecuted CI.

## Purpose

Callback/event bridges and explicit ownership/lifetime rules.

## API and contract expectations

- Expose general-purpose interfaces that are usable without an Atto commercial account.
- Document data/ownership semantics, error behavior, and supported runtimes.
- Keep protocol and serialization details portable across relevant AttoLang backends.

## Development and testing

Use checked-in implementation and CI for actual commands. Add behavior-focused tests, including negative cases and lifecycle edge cases; distinguish local unit tests from executed multi-backend conformance.

## Project status

This describes intended scope, not a verified feature matrix. Consult the source tree and exact-commit CI results for implementation status.

## Ecosystem

- [AttoLang](https://github.com/atto-lang)
- [Language specification](https://github.com/atto-lang/atto-spec)
- [Cross-platform conformance](https://github.com/atto-lang/atto-platform-conformance)

## Repository ownership and contribution routing

**Belongs here:** Host callback interop adapters, listener registration/unregistration and explicit callback ownership/lifetime rules.

**Belongs elsewhere:** Core stream operators in atto-rx, channels in atto-rx-channels and async task composition in atto-rx-tasks.

**Security and portability boundary:** Never smuggle lexical closures through serializable actor messages; make unsubscribe and late callback behavior race-safe with generation tokens.

AttoLang is the canonical project name; new source, examples and documentation use `.atto` and the `atto-lang` repository organization. This README defines scope, not feature readiness.

**Acceptance:** name exact source SHA/tree, runtime/toolchain, positive and negative checks and execution receipt before claiming support. Host-only tests and empty CI steps do not prove guest execution.

## Legacy migration provenance and gates

The original `ores-truffle-oreslang/rx-ores-callbacks` repository is archived; this AttoLang repository has a separate numeric GitHub identity. Historical `.ores` files, imports, package names and CLI identifiers are compatibility history, not evidence of current `.atto` execution. Safe reactive callback bridges and explicit ownership tests belong here; lexical closures must not cross isolated actor channels.

[atto-lang](https://github.com/atto-lang) owns language libraries, compilers, tooling, tests and examples; [atto-co](https://github.com/atto-co) owns hosted deployment, tenant infrastructure, identity and billing. A future original-ID transfer or product carve-out requires separate source/target owner and independent security approval. Inventory exact SHA/tree, numeric ID, visibility, permissions, protections, PRs, releases, packages, dependencies, runners, secrets, applications, webhooks, Pages and rollback owner; verify preservation and rerun exact-head tests after an actual transfer. Never mirror private source without authorization. Zero-step jobs are NOT_EXECUTED; host-only checks do not establish native guest/compiler execution.
