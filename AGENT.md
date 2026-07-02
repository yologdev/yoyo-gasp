# AGENT — yoyo 🐙

```yaml
spec_version: 1
agent_id: yoyo
identity_hash: 69d0cdeed76978411b206e870decfa98d2252bdd15cabd22cda2655c41a44dba
executor: .agent/config.toml
```

This repo is **yoyo's durable state** per the [GASP protocol](https://github.com/yologdev/gasp):
identity, skills, memory, and the append-only semantic event log that folds into
yoyo's lineage graph. The **executor** — the self-evolving runtime yoyo works on —
lives in [yologdev/yoyo-evolve](https://github.com/yologdev/yoyo-evolve); patches
recorded here pin its commits as artifacts. Clone this repo and fold the log to
restore yoyo anywhere, on any conformant runtime.

## Provenance

Seeded 2026-07-02 from `yologdev/yoyo-evolve@582147ad5728b9a74477729e67e46df2d2ac8ba0`
(day-file state as of that commit). Identity files are byte-for-byte copies;
`identity/PRINCIPLES.md` is yoyo-evolve's `ECONOMICS.md`. `memory/facts.jsonl`
carries the original `memory/learnings.jsonl` lines verbatim (yoyo's historical
learning format); facts appended after seeding follow the GASP fact envelope
(`id`, `ts_ms`, `text`, `derived_from`, `supersedes`).

## Locations

| GASP role | path | notes |
|---|---|---|
| event log | `state/events.jsonl` | source of truth, append-only |
| identity | `identity/` | human-gated; hash above, recipe below |
| skills | `skills/` | versioned; one change per commit |
| facts | `memory/facts.jsonl` (+ `memory/social_facts.jsonl`) | append-only derived layer |
| memory synthesis | `memory/active_memory.md` (+ `active_social_memory.md`) | regenerable projection |
| journal | `journal/` | regenerable projection |

## Identity hash recipe

SHA-256 over each `identity/` file's relative path followed by a newline and its
bytes, in sorted path order:

```
for f in $(find identity -type f | sort); do printf '%s\n' "$f"; cat "$f"; done | shasum -a 256
```

An identity change updates `identity/`, this hash, and appends a `decision`
event — all in one human-gated commit (GASP Part I, commit rule 4).
