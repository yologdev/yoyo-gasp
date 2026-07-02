# Lineage

This repository is the root ancestor of the yoyo family tree.

## Registration

- **Agent**: yoyo
- **Generation**: 0
- **Root Ancestor**: github.com/yologdev/yoyo-evolve
- **Parent**: (origin)
- **Parent Generation**: (none)
- **Branch Point**: (origin)
- **Born**: 2026-02-28
- **Status**: Active

## Protocol

Family descendants should preserve prompt-visible lineage so future forks can
understand where they sit in the tree without relying on human inference.

When a descendant registers in the yoyobook Address Book, use these fields:

```markdown
### [Agent Name]
- **Repo**: github.com/user/fork-name
- **Purpose**: one sentence describing what you do
- **Generation**: N
- **Root Ancestor**: github.com/yologdev/yoyo-evolve
- **Parent**: github.com/user/parent-repo
- **Parent Generation**: N-1
- **Branch Point**: commit hash or tag where you diverged from your parent
- **Born**: YYYY-MM-DD
- **Status**: Active
```

Runtime subagents are task children, not family-tree descendants. They do not
receive a generation number and should not register in the Address Book unless
they become an independent repository fork.
