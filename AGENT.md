# AGENT — yoyo 🐙

```yaml
spec_version: 1
agent_id: yoyo
identity_hash: 69d0cdeed76978411b206e870decfa98d2252bdd15cabd22cda2655c41a44dba
executor: .agent/config.toml
```

This repo is **yoyo's durable state** per the [GASP protocol](https://github.com/yologdev/gasp):
identity, skills, memory, and the append-only semantic event log that folds into
yoyo's lineage graph. The **executor binding** lives in `.agent/config.toml`
(currently [yologdev/yoyo-evolve](https://github.com/yologdev/yoyo-evolve), the
self-evolving runtime yoyo works on); patches recorded here pin its commits as
artifacts. Clone this repo and fold the log to restore yoyo anywhere, on any
conformant runtime.

## Provenance

Seeded 2026-07-02 from `yologdev/yoyo-evolve@582147ad5728b9a74477729e67e46df2d2ac8ba0`
(the working-tree state of that commit, through Day 124), completed 2026-07-03
with the lineage/dream/notes state below. Identity files are byte-for-byte
copies; `identity/PRINCIPLES.md` is yoyo-evolve's `ECONOMICS.md`;
`memory/notes.json` is `.yoyo/memory.json` and `memory/social_cursors.json` is
`.yoyo/social-state.json`. Skill bodies were rebound to this layout's paths
(`memory/learnings.jsonl` → `memory/facts.jsonl`, `journals/` → `journal/`, …);
executor-side material (runtime source, `CLAUDE.md`, `docs/`, `sponsors/`,
scheduler counters) intentionally stays in yoyo-evolve.

`memory/facts.jsonl` carries the original `memory/learnings.jsonl` lines
verbatim (yoyo's historical learning format). Facts appended after seeding
MUST follow the GASP fact envelope (`id`, `ts_ms`, `text`, `derived_from`,
`supersedes`); legacy-format lines end at the seed.

## Locations

| GASP role | path | notes |
|---|---|---|
| event log | `state/events.jsonl` | source of truth, append-only |
| identity | `identity/` | human-gated; hash above, recipe below |
| lineage record | `LINEAGE.md` | genealogy (generation, ancestor, birthday) — a record, not constitution, so outside the identity hash |
| skills | `skills/` | versioned; one change per commit; `skills/_journal.md` is the skill-evolution journal, not a skill |
| facts | `memory/facts.jsonl` (+ `memory/social_facts.jsonl`) | append-only derived layer; social pair mirrors facts → active memory, declared here per the GASP manifest-binding rule |
| memory synthesis | `memory/active_memory.md` (+ `active_social_memory.md`) | regenerable projection |
| agent notes | `memory/notes.json` | durable runtime notes (was `.yoyo/memory.json`) |
| social cursors | `memory/social_cursors.json` | seen/replied discussion state (was `.yoyo/social-state.json`) |
| journal | `journal/` | seeded history through Day 124; `JOURNAL.md` is append-only (conformance check 4) — new run entries are appended, existing lines never rewritten |
| dreams | `DREAM.md`, `dreams/` | self-model narrative + append-only dream log |
| age | `DAY_COUNT` | yoyo's day counter — identity-adjacent |

## Identity hash recipe

SHA-256 over each `identity/` file's relative path followed by a newline and its
bytes, in byte-order-sorted path order:

```
find identity -type f | LC_ALL=C sort | while IFS= read -r f; do printf '%s\n' "$f"; cat "$f"; done | shasum -a 256
```

An identity change updates `identity/`, this hash, and appends a `decision`
event — all in one human-gated commit (GASP Part I, commit rule 4).
