# Credential safety

Credentials belong in the host secret store, never canonical GASP, shared memories, prompts, checkpoint payloads or model-visible environment dumps. The repository is public. Gitignore is an accidental-staging guard, not a credential detector.

## Local enforcement

`python3 scripts/check-secrets.py --mode staged` scans the complete index snapshot, including forced-added ignored files. It rejects local configuration/session/key paths, symlinks/submodules, recognizable credential patterns and exact secret-like environment variable values (including common encodings). It uses Gitleaks defaults with redacted output, disables inline bypass comments and repository ignore files, and blocks on scanner errors. It prints filenames/rule IDs only, never matching text. Pattern scanning cannot guarantee detection of every opaque credential or wallet mnemonic.

Install a checksum-verified Gitleaks release on PATH or at `.agent/bin/gitleaks`, then run `git config core.hooksPath .githooks`. Hooks run the staged gate before commit and the full-history gate before push. Local hooks can be bypassed and are not installed by cloning: every writer must explicitly run the scanner before commit/push regardless of hooks. Scanners and hooks must be controlled by the host, not modifiable by the task they check.

## Canonical writer and recovery requirements

The canonical writer must use an allowlist of output paths, never `git add .`, and scan the staged bytes plus all outgoing history before pushing. Pass current credentials to the isolated scanner for exact-value detection, not into the agent prompt. A scan failure must retain the outbox unacknowledged and block persistence/publication; do not silently redact an already-hashed checkpoint and claim it is unchanged.

The sandbox should receive narrowly scoped tool access through host proxies. Never snapshot its entire home directory or environment. Export only explicitly approved workspace paths. Scan all checkpoint payloads before upload, including decoded session text and unpacked archives; encrypt private artifacts at rest and keep raw sessions out of public GASP/content exports. R2 privacy is not permission to retain credentials. A model prompt or instruction to avoid secrets is insufficient enforcement.

Enable GitHub secret scanning and push protection through a repository administrator. PR/CI scans are an additional detection layer: scans triggered after push cannot prevent the initial disclosure. All evolution, social, dream and manual writers must adopt the pre-publication gate before claiming repository-wide enforcement.

If a genuine credential is found in committed history, stop affected writers, revoke/rotate it, investigate exposure, then coordinate history cleanup. Never print the credential or upload unredacted scanner reports. Do not rewrite the append-only canonical history automatically.

## Credential-free task sessions

Cloudflare task execution should put the model/provider key behind a host-side model gateway and service credentials behind narrowly scoped tool proxies. The CLI process must not receive raw provider, GitHub, X or wallet credentials in its environment, arguments, filesystem, prompt, tool output or saved session. If a gateway requires task authorization, use a short-lived scoped capability supplied by the host transport; never serialize it into model messages or checkpoints. Restrict task networking to the intended gateways. Do not expose the host secret store or credential-bearing git configuration through filesystem mounts.

A shell-capable agent can read its own environment. Merely moving a key from a prompt to an environment variable does not isolate it. If an adapter cannot avoid exposing credentials to the agent process, it must report that limitation and cannot claim credential-free sessions. Do not implement this by rewriting the evolving CLI: adapt the host gateway and harness interfaces, or leave support pending for Yoyo to evolve.

Recovery exports must use approved paths rather than whole-home/container snapshots. Scan the serialized session and unpacked workspace before hashing or upload; a clean transcript does not prove its workspace is clean. Secret-like values detected in a session must block its export rather than be promoted into shared memory.

## Rollout scope

This repository provides ignore rules, a scanner and opt-in local hooks. Cloning does not enable hooks, and no yoyo-evolve source, harness or workflow is changed by this rollout. Existing autonomous writers are unchanged. Host-side gateway isolation for future Cloudflare CLI tasks remains an implementation requirement, not a deployed guarantee.

The account used to inspect GitHub has push but no repository administration permission; secret-protection settings were not visible. Their absence in the response does not prove they are disabled. An administrator can enable repository push protection independently of executor changes.
