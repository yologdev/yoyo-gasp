---
name: release
description: Evaluate readiness and publish to crates.io
tools: [bash, read_file, write_file]
origin: yoyo
status: active
score: 0.59
uses: 1
wins: 1
last_used: "2026-05-13T19:45:37Z"
last_evolved: "2026-05-19"
parent_pattern_key: null
keywords: ["cargo publish", "cargo publish --dry-run", "git tag v", "publish to crates"]
---

# Release Decision

You can publish yourself to crates.io. This is permanent.
You cannot unpublish. Treat this seriously.

## Gate (ALL must pass — no exceptions)
- cargo build with zero warnings
- cargo test with zero failures
- cargo clippy with zero warnings
- cargo fmt -- --check passes
- At least 10 tests exist
- CHANGELOG.md exists and is current
- README.md accurately describes what you can do right now

## How to check
Run this and every line must say PASS:
  cargo build 2>&1 | tail -1
  cargo test 2>&1 | tail -1
  cargo clippy --all-targets 2>&1 | grep -c warning | xargs test 0 -eq && echo PASS
  cargo fmt -- --check && echo PASS
  cargo test 2>&1 | grep "test result"
  # must show at least 10 tests

## How to release
1. Verify ALL gates above
2. Update version in Cargo.toml (semver: 0.1.0, 0.2.0, etc)
3. Write CHANGELOG.md entry
4. git tag v[version]
5. cargo publish
6. Write in your journal: what version, why now, what's in it

## Version rules
- 0.x.y — you're pre-1.0 until you're truly production-ready
- Bump minor (0.1 → 0.2) for new features
- Bump patch (0.1.0 → 0.1.1) for bug fixes only
- Never release twice in one session

## If publish fails
Journal it. Don't retry in the same session. Figure out
why tomorrow.
