---
name: skill-creator
description: Scaffold a new yoyo skill when a human or community issue asks for one ("add a skill for X", "create a skill that does Y"). Generates correct frontmatter, validates, writes to disk.
tools: [bash, read_file, write_file, sub_agent]
core: true
origin: creator
---

# Skill Creator

You are creating a new yoyo skill **on demand**, in direct response to an explicit request — either from the human creator or from a community issue asking for a new capability.

## skill-creator vs skill-evolve

These are complementary, not redundant. Use the right one:

| Question | skill-creator (this skill) | skill-evolve |
|---|---|---|
| Who triggers it? | Human creator OR community issue (explicit ask) | GitHub Actions cron (autonomous) |
| When does it run? | Inside a normal evolve session, on demand | Hourly cron at `:30`, gated by 5-session counter + 24h cooldown |
| What signals does it use? | The user's request | Past-session evidence (learnings, journal, audit-log) |
| Recurrence gate? | No (human is in the loop) | Yes (≥3 sessions for create) |
| Diff-scope guard? | None — runs in evolve session | Yes — `scripts/skill_evolve.sh` enforces |
| Auto-commit? | Yes (inside evolve session's commit flow) | Yes (after diff-scope + build/test gates) |

**Rule of thumb**: if no human asked, you're not creating a skill — you're noticing a pattern. Write it to `memory/learnings.jsonl` with a `pattern_key` and let skill-evolve pick it up on the next cycle.

## When NOT to use this skill

- You're inside a `scripts/skill_evolve.sh` cycle. Use the Create branch in `skills/skill-evolve/SKILL.md` instead — it has the right gates (recurrence, dedup, ≤25 cap).
- You noticed a recurring pattern but no one asked. Write a learning with `pattern_key`; skill-evolve owns autonomous creation.
- The user asked for a one-off helper that won't be invoked again. Just write it inline; don't litter `skills/`.

## When to use this skill

- The human creator (Yuanhao) tells you "scaffold a new skill for X"
- A community issue says "please add a skill for X" and you decide during a normal evolve session that the request is concrete enough to act on
- You're installing a third-party skill from outside the repo (uses `origin: marketplace` or `origin: gh:author/repo`)

## Procedure

### 1. Capture intent

Ask (or infer from issue) — and write down explicit answers before writing any code:

- **What does this skill do?** (one sentence)
- **When should it trigger?** (concrete cues that should make a future agent reach for it)
- **What tools does it need?** (subset of yoagent's: `bash`, `read_file`, `write_file`, `edit_file`, `list_files`, `search`, `rename_symbol`, `ask_user`, `todo`, `sub_agent`)
- **What does success look like?** (how does the agent know the skill worked?)

### 2. Determine `origin:`

| Asker | Use of skill | `origin:` | `core: true`? |
|---|---|---|---|
| Human creator (Yuanhao) | Foundational capability, not delegated to autonomous evolution | `creator` | yes |
| Human creator | Useful but yoyo-evolvable later | `creator` | no |
| Yoyo (during issue response) | Domain capability for yoyo's own future use | `yoyo` | no |
| External source | Installed third-party skill | `marketplace` (or `gh:author/repo`) | no |

The default if you're unsure: `origin: yoyo` for yoyo-decided creations, `origin: creator` for human-driven creations. Never default to `marketplace`.

**HARD PRECONDITION on `origin: marketplace` / `origin: gh:…`** (closes a backdoor — these origins are off-limits to skill-evolve, so they must come from a real upstream, not be self-granted):

- The skill content MUST be downloaded in this same session from a verifiable URL (curl/git/gh). Record the URL in the skill's body under a `## Source` section.
- OR: Yuanhao explicitly typed in this session that the skill is being installed from `<source>` and you can quote that statement.

If neither holds, refuse and pick `creator` or `yoyo` instead. A skill yoyo wrote itself but tagged `marketplace` would be a permanent un-evolvable artifact — that's a hole in the safety design.

### 3. Pick a kebab-case name

Format: `<verb>-<object>` (e.g., `bisect-flaky-test`, `compose-changelog`, `triage-pr`). Single-word names are okay only for genuinely-broad scopes (`research`, `release`).

Check for collision before going further:

```bash
ls skills/ | grep -i "<your-name-stem>"
```

If a similar name exists, **stop and ask** whether to refine the existing one instead — the answer is usually yes.

### 4. Write the description (≤200 chars)

This is the most important field. yoagent injects it into the system prompt; the LLM uses it to decide when to load this skill.

Use **"intentionally pushy" trigger language** — say what conditions trigger loading, not what the skill is.

| WEAK (descriptive) | STRONG (pushy) |
|---|---|
| "A skill for working with flaky tests" | "Investigate flaky tests by isolating, repeatedly running, and bisecting recent commits" |
| "Helps with releases" | "Validate readiness and publish to crates.io: gate checks (build/test/clippy/fmt) before any `cargo publish`" |

Hard cap: 200 chars. The Hermes ecosystem documented description-truncation failures (#13944) at higher lengths.

### 5. Pick keywords (only if `origin: yoyo`)

For `origin: yoyo` skills, list 3–5 distinctive substrings that would appear in a session's `audit.jsonl` IF this skill were used. skill-evolve uses these to compute `last_used` / `uses` / `wins`.

Examples:
- `release` skill: `["cargo publish", "crates.io", "git tag v"]`
- `social` skill: `["gh api graphql", "discussion", "addDiscussionComment"]`

Skip the `keywords:` field for `origin: creator` skills (skill-evolve can't refine them anyway).

### 6. Generate the SKILL.md scaffold

Choose the template that matches `origin:`.

**For `origin: creator`:**
```yaml
---
name: <name>
description: <pushy description ≤200 chars>
tools: [<subset of yoagent tools>]
core: true
origin: creator
---

# <Title>

## When to use
<concrete trigger conditions — when should the agent reach for this?>

## Quick reference
<one-screen cheat sheet — verbs, file paths, common commands>

## Procedure
<numbered steps the agent should follow>

## Pitfalls
<known failure modes — what to watch out for>

## Verification
<how the agent confirms success>
```

**For `origin: yoyo`:**
```yaml
---
name: <name>
description: "[CANDIDATE — unreviewed] <pushy description ≤200 chars>"
tools: [<subset of yoagent tools>]
origin: yoyo
status: candidate
score: 0.5
uses: 0
wins: 0
last_used: null
last_evolved: <today, YYYY-MM-DD>
parent_pattern_key: <kebab-case verb.object — describes the recurring pattern this skill addresses>
keywords: ["<distinctive 1>", "<distinctive 2>", "<distinctive 3>"]
---

# <Title>

(same body sections as above)
```

The `[CANDIDATE — unreviewed]` description prefix is critical for `origin: yoyo` skills — it tells future sessions to treat the skill as experimental until it proves itself (≥2 successful invocations → `status: active`).

### 7. Validate before commit

Run all of these. If any fails, fix before committing — do not push a malformed skill.

**First**, set the skill name as a shell variable so the rest of the block is copy-paste-safe (avoids the trap of literal `<name>` strings reaching the shell):

```bash
export SKILL_NAME="<your-kebab-case-name>"   # e.g., bisect-flaky-test
test -d "skills/$SKILL_NAME" || { echo "ERROR: skills/$SKILL_NAME doesn't exist"; exit 1; }
```

```bash
# YAML frontmatter parses, ≤1900 chars (defends against Hermes #7390 truncation)
python3 - "$SKILL_NAME" <<'PYEOF'
import re, sys
name = sys.argv[1]
content = open(f"skills/{name}/SKILL.md").read()
m = re.match(r"---\n(.*?)\n---\n", content, re.DOTALL)
if not m:
    sys.exit("ERROR: no frontmatter")
fm = m.group(1)
if len(fm) > 1900:
    sys.exit(f"ERROR: frontmatter too long: {len(fm)} chars (cap 1900)")
# Crude key:value sanity
for line in fm.splitlines():
    if line.strip() and ":" not in line:
        sys.exit(f"ERROR: invalid frontmatter line: {line!r}")
print("frontmatter OK")
PYEOF

# Description ≤200 chars
desc=$(grep '^description:' "skills/$SKILL_NAME/SKILL.md" | head -1 | sed 's/^description: *//')
[ "${#desc}" -le 200 ] || { echo "ERROR: description ${#desc} chars > 200"; exit 1; }

# Body ≤5000 words (matches skill-evolve's cap)
body_words=$(awk '/^---$/{n++; next} n>=2' "skills/$SKILL_NAME/SKILL.md" | wc -w)
[ "$body_words" -le 5000 ] || { echo "ERROR: body $body_words words > 5000"; exit 1; }

# Directory name matches frontmatter name
fm_name=$(grep '^name:' "skills/$SKILL_NAME/SKILL.md" | head -1 | sed 's/^name: *//' | tr -d '"' )
[ "$fm_name" = "$SKILL_NAME" ] || { echo "ERROR: dirname/name mismatch: dir=$SKILL_NAME fm=$fm_name"; exit 1; }
```

### 8. Smoke-test the skill loads via yoagent

```bash
cargo test --quiet --test integration skills_directory_loads_via_yoagent_skillset
```

This regression test loads every `skills/*/SKILL.md` via `yoagent::skills::SkillSet::load`. If your new skill breaks parsing, the test fails immediately. **If it fails, do not commit** — fix the frontmatter first.

### 9. Commit

```bash
# Reuse $SKILL_NAME from step 7
git add "skills/$SKILL_NAME/"
git commit -m "skill-creator: add $SKILL_NAME (origin: <creator|yoyo|marketplace>)"
```

The commit goes into the current evolve session's commit history. No separate push — the evolve session's normal end-of-session push will carry it.

### 10. Note in the journal

If you (yoyo) created this skill in response to a community issue, **also write a journal entry** explaining what was added and why. This is what `communicate` skill is for.

## Pitfalls

- **Don't auto-create skills mid-session without an explicit request.** Yoyo's autonomous self-creation belongs in skill-evolve, which has the right safety gates (recurrence, cooldown, dedup, blast-radius limits). Using skill-creator without a clear human ask is a hard rule violation.
- **Don't set `origin: yoyo` for skills the human creator explicitly asked for.** Those are `origin: creator` (and probably `core: true`). The reverse is also true — don't set `origin: creator` on something yoyo decided to make.
- **Don't omit `keywords:` for `origin: yoyo` skills.** Without keywords, skill-evolve can't compute usage signals; the skill becomes invisible to the scoring loop.
- **Don't create a skill that overlaps an existing one.** ≥3 keyword overlap with an existing skill's "When to use" → refine that one instead. Same rule skill-evolve uses.
- **Don't skip step 7 validators.** Silent frontmatter truncation, description routing failures, body-token blow-ups — all real failure modes documented in the Hermes ecosystem (#7390, #13944, #14405).
- **Don't write a skill body that exceeds 5000 words.** Loaded into the prompt every session = cumulative token cost. Be brutal about brevity.

## Verification

A skill is well-formed when:

- The integration test `skills_directory_loads_via_yoagent_skillset` passes.
- The skill's directory name matches the `name:` frontmatter field.
- All required frontmatter fields are present (per origin tier — see step 6 templates).
- Description ≤200 chars.
- Frontmatter ≤1900 chars total.
- Body ≤5000 words and contains the five sections: When to use / Quick reference / Procedure / Pitfalls / Verification.
- For `origin: yoyo` skills: `keywords:` has ≥3 entries.
- The `cargo build` and `cargo test` gates that follow your commit are still green.

## What this skill deliberately does NOT do

- **No eval/benchmark pipeline.** Anthropic's `skill-creator` includes synthetic prompts + grader subagent + benchmark.json aggregation. That capability lives in skill-evolve's Refine action (steps R1–R6) where the snapshot+A/B pattern can compare a candidate against the prior version. Adding it to skill-creator would duplicate; new skills don't have a "prior version" to A/B against anyway.
- **No browser eval viewer.** Yoyo runs autonomously in CI; no browser. If you need to compare versions, use `git diff`.
- **No autonomous pattern detection.** That is skill-evolve's job. Skill-creator runs only when explicitly invoked.
- **No retirement / deprecation logic.** Lifecycle management is skill-evolve's job. Skill-creator only creates; it does not delete or downgrade.

If you find yourself wanting any of these capabilities, ask yourself first whether you're really inside a skill-evolve cycle.
