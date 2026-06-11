# Vendored Claude Code Skills

This folder holds skill copies activated for sessions opened in this repo. Each subdirectory is one skill; Claude Code loads them on demand.

## Contents

| Skill | Purpose | Vendored from |
|---|---|---|
| `release/` | Release atomic-agents to PyPI and GitHub | (repo-native) |
| `create-atomic-agent/` | Scaffold a new `AtomicAgent[In, Out]` — schemas, config, prompt, client wiring | `claude-plugin/atomic-agents/skills/create-atomic-agent/` |
| `create-atomic-tool/` | Scaffold a new `BaseTool[In, Out]` subclass with schemas, config, `run()` | `claude-plugin/atomic-agents/skills/create-atomic-tool/` |
| `framework/` | Umbrella reference skill + 11 deep-dive docs (agents, tools, schemas, prompts, memory, hooks, orchestration, providers, context-providers, project-structure, testing). Auto-fires when atomic-agents code is in context. | `claude-plugin/atomic-agents/skills/framework/` |

## Why vendored copies exist

The canonical home of these scaffolding skills is `claude-plugin/atomic-agents/skills/`. They ship there as part of the official **atomic-agents** Claude Code plugin (MIT-licensed, by BrainBlend AI).

Copying them under `.claude/skills/` makes them active **without** requiring contributors to run `/plugin marketplace add ...` or wire the plugin into Claude Code settings. They load automatically on any session opened against this repo.

**Trade-off:** the copies will drift from upstream over time. Periodically diff against `claude-plugin/atomic-agents/skills/` and re-sync. The preferred long-term path is to enable the plugin via `.claude/settings.json` instead of vendoring — see `claude-plugin/atomic-agents/README.md` for the config block.

## Attribution

The vendored skills are © BrainBlend AI, licensed MIT. See:
- `claude-plugin/atomic-agents/LICENSE` (license text)
- `claude-plugin/atomic-agents/.claude-plugin/plugin.json` (plugin manifest)

No code changes were made during vendoring — the copies are byte-identical to the source at the time they were added.
