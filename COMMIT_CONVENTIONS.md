# Commit Conventions

## Format
<type>(<scope>): <short description>

## Types
- feat: new functionality
- fix: bug fix
- test: adding or fixing tests
- docs: documentation only (PLAN.md, NOTES.md, CLAUDE.md, README.md)
- config: changes to configs/main.yaml or other config files
- chore: maintenance (gitignore, requirements, etc.)
- refactor: code restructure with no behaviour change

## Scopes
- stage1, stage2, stage3, stage4, stage5, stage6, stage7
- algorithms, metrics, data, experiments, utils, tests, report

## Examples
feat(stage2): implement CountMinSketch with HashFamily
test(stage2): add 30 unit tests across all 5 algorithms
fix(stage2): clip CountSketch negative estimates in query()
docs(plan): update stage tracker, log Stage 2 handback
chore: add .gitignore, commit conventions

## Rules
- Subject line max 72 characters
- Use imperative mood: "add" not "added", "fix" not "fixed"
- One logical change per commit — do not bundle unrelated changes
- Always commit PLAN.md and NOTES.md updates together as a single docs commit
- Never commit: .venv/, data/raw/, results/, plots/
- Always commit: src/, tests/, configs/, PLAN.md, CLAUDE.md, NOTES.md