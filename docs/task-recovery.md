# Yoyo task recovery binding

Status: proposed binding to GASP's optional draft `gasp.task-recovery/v1`; not a claim of deployed recovery support. Protocol: https://github.com/yologdev/gasp/blob/main/extensions/TASK_RECOVERY.md.

## Ownership

Yoyo evolves the Rust CLI. Human maintenance is limited to its harness files; this binding does not authorize manual CLI-source changes. The cloud harness owns task assignment, isolated workspaces, persistence, permissions and external publication. GASP owns portable semantic history.

## Task layout and restore

Every assignment receives a stable task ID and each execution a new run ID. Record domains such as social, research or coding in task metadata; use explicit task/run relations. All domains share the canonical append-only log and coordinated writer. Non-evolution tasks must not manufacture evolution patch/evaluation records.

Proposed committed manifests: `execution/tasks/<task-id>/checkpoints/<checkpoint-id>.json`, referenced by hash from the producing run using the protocol artifact kind. The folded task metadata is the latest-checkpoint index; no separate mutable file is authoritative. Large private session/workspace artifacts may use R2 through a resolver/exporter. These paths are conventions to implement, not existing artifacts.

A sandbox restores into a task-specific workspace, separate from the canonical GASP checkout. Provide identity and skills from verified snapshots and book/memory retrieval with recorded source revisions. Do not cd every task into one writable GASP root. The global writer alone merges canonical events and eligible learned facts. Private transcripts and required checkpoints must not enter public dashboard/content exports; export only explicitly allowed document classes.

## Existing CLI support checked 2026-09-11

The installed CLI reports v0.1.17. The local source implements `/save <path>` and `/load <path>` for custom conversation JSON files. `--continue` restores `.yoyo/last-session.json` in the working directory, falling back to `yoyo-session.json`. No `--session-file` flag was found in the checked help/config. A conversation save is not a workspace snapshot or full process checkpoint.

The harness can use a controlled interactive session with explicit save/load paths, or restore a validated session to the task workspace's default path before `--continue`. It must verify restore success: the current loader warns on failure and continues. Piped input is treated as a task prompt, not a REPL command script; do not pipe `/save` or `/load` and assume they execute as commands. Do not assume single-prompt or stream-JSON mode saves resumable state automatically. Verify checkpoint creation before declaring any unattended adapter session-recoverable.

The existing local summon script only prepares context and launches the CLI; it is not a task recovery adapter. A cloud harness should enforce identity hash verification, retain task-specific CWD/session files, select journal entries chronologically, pin the executor build and pass provider/model explicitly. Any CLI capabilities missing after harness validation belong in Yoyo's self-evolution backlog.

## Recovery policy

Follow the protocol's persist-first/commit-reference/acknowledge order. Use a per-task lease and fencing generation, expected-parent comparison and the shared canonical writer. Resume creates a new run under the same task. Restore only that task's conversation and workspace; record explicit shared-memory refreshes and session versus semantic mode. Reconcile Twitter and other external effects against their durable action ledger before resuming pending calls.

Required checkpoint artifacts survive sandbox deletion and remain retained while recovery is advertised. Leases and credentials are never committed. Budget and permissions are re-evaluated by the host on each resume. CLI checkpoints alone never authorize publishing, modifying identity, or writing evolution verdicts.

## Implementation acceptance

Before activation, demonstrate the protocol acceptance cases, especially two-task isolation, custom save/load success and failure, unattended save behavior, container deletion and restore, external artifact export/import, and uncertain-publication reconciliation. Keep current Twitter production behavior until a replacement adapter passes these checks. No runtime or canonical task-event changes are made by this documentation.

The published protocol draft was introduced in `yologdev/gasp@f24bb14`. Credential isolation follows [credential-safety.md](credential-safety.md). Recovery support remains pending harness acceptance tests; no Rust CLI changes are authorized by this binding.


## Isolated harness evidence — 2026-09-11

The [Cloudflare recovery lab](https://github.com/yuanhao/yoyo-cloudflare/tree/main/labs/recovery) passed real unmodified CLI save/load and isolated task restoration after container destruction, using synthetic state and a local simulated model. [CI evidence](https://github.com/yuanhao/yoyo-cloudflare/actions/runs/34579498100) and remote reports are retained there. This is partial acceptance evidence: no canonical GASP task checkpoint writer, complete extension manifest, writer-fencing tests, real model gateway or production task execution is deployed. Existing evolution and Twitter behavior are unchanged.
