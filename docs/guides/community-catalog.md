# Community Catalog

A curated list of community-built **skills**, **atomic-agents tools**, and **plugin bundles** you can pull from when building with Atomic Agents and Claude Code.

This is a **discovery aid**, not vendored code. Links lead to upstream repos — check each project's license before copying anything into your own codebase. Inclusion here is not an endorsement.

> Snapshot date: 2026-05-26. The Claude Code ecosystem moves fast; expect this list to drift. PRs welcome.

## Start here — official skills already in this repo

Before browsing the community catalog, know that this repo **already ships official scaffolding skills** for the framework. They live at `claude-plugin/atomic-agents/skills/` and a vendored copy is active under `.claude/skills/` (see `.claude/skills/README.md`):

- `create-atomic-agent` — scaffold an `AtomicAgent[In, Out]`
- `create-atomic-tool` — scaffold a `BaseTool[In, Out]`
- `create-atomic-schema`, `create-atomic-context-provider`, `new-app`
- `framework` — umbrella skill with 11 deep-dive reference files

For most "I want to build something with atomic-agents" needs, these are better than anything in the community catalog below. The catalog is here for everything else (general-purpose skills, plugin bundles, cross-project tooling).

## How to use this catalog

- **Browsing for ideas?** Skim the categories below — each entry is one line so you can scan quickly.
- **Want to install a skill?** Most community skills live in repos that expose `.claude/skills/<name>/SKILL.md`. Copy the folder into your own `~/.claude/skills/` or this repo's `.claude/skills/`, then restart Claude Code so it picks them up.
- **Want a whole plugin pack?** Use the Claude Code `/plugin` command pointed at one of the marketplace repos in Category C.
- **Want an atomic-agents tool?** Use the `atomic-assembler` CLI for the official forge tools. Community tools (Category B) you'll need to vendor by hand — the ecosystem doesn't have a registry yet.

---

## Category A — Claude Code Skills (`SKILL.md`)

The Claude Code skills ecosystem is dense and active. Start with the official examples, then dip into the curated lists.

- **[anthropics/skills](https://github.com/anthropics/skills)** — Anthropic's official public examples. _The canonical reference for SKILL.md structure and best practices._
- **[hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)** — The largest curated index of skills, hooks, slash commands, and plugins. _Best single entry point if you don't know what you're looking for yet._
- **[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)** — 300+ production-ready skills organized by function (Engineering, Product, Research, etc.). _Useful when you want a specific role-shaped skill._
- **[travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)** — Curated list focused on Claude-Code skill customization. _Good secondary index alongside hesreallyhim's list._
- **[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)** — Skills focused on workflow customization. _Useful for integration-heavy use cases._
- **[daymade/claude-code-skills](https://github.com/daymade/claude-code-skills)** — Community collection demonstrating the standard skills + bundled MCP server pattern. _Good study example if you're building skills that talk to MCP servers._
- **[obviousworks/Claude-AI-skills-collection-2026](https://github.com/obviousworks/Claude-AI-skills-collection-2026)** — Curated collection with clear submission guidelines. _Worth watching for new additions._
- **[Masriyan/Claude-Code-CyberSecurity-Skill](https://github.com/Masriyan/Claude-Code-CyberSecurity-Skill)** — 15 cybersecurity-focused skills (offensive, SOC, threat hunting). _A solid example of a vertical skill pack._
- **[affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)** — Hackathon-built collection covering performance, memory, security, and research workflows. _Interesting design ideas if you want to study skill-to-skill composition._
- **[jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills)** — Massive aggregation (2,800+ skills) with a CLI installer (`ccpi`). _Use when you want a marketplace experience rather than a curated list._

---

## Category B — Atomic Agents Tools (`BaseTool` subclasses)

**Heads up: this ecosystem is thin.** Most tool development happens inside the official `atomic-forge` and the framework currently lacks a community "awesome list." If you build a useful tool, consider publishing it — there's an open niche here.

- **[BrainBlend-AI/atomic-agents/atomic-forge](https://github.com/BrainBlend-AI/atomic-agents/tree/main/atomic-forge)** — The official tool collection: calculator, web search (SearXNG, Tavily), PDF reader, Wikipedia, YouTube transcript, weather, arXiv, and more. _The starting point for any tool need — check here before you build._
- **[atomic-forge tool structure guide](../../atomic-forge/guides/tool_structure.md)** — Local guide on what a tool looks like and the standard layout. _Read this first if you plan to write your own tool._
- **[w3bwizart/Atomic_Agents_Learn](https://github.com/w3bwizart/Atomic_Agents_Learn)** — Community learning repo with custom agent and tool examples. _Useful for seeing how someone outside the core team structures their tools._
- **[mrseanryan/gpt-multi-atomic-agents](https://github.com/mrseanryan/gpt-multi-atomic-agents)** — A multi-agent extension framework built on `atomic_agents`, Instructor, and Pydantic. _Not a tool itself, but the closest thing to a third-party framework extension — worth a look if you outgrow single-agent patterns._

> **Gap noted:** There is no `awesome-atomic-agents` list at time of writing. If you start one, link it back here.

---

## Category C — Plugin Marketplaces & Bundles

Plugin marketplaces ship bundles of skills + agents + commands together, installable via Claude Code's `/plugin` command. The format stabilized around the `.claude-plugin/plugin.json` manifest in late 2025.

- **[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)** — Anthropic-managed directory of reviewed plugins. _Start here. Highest quality bar._
- **[claudemarketplaces.com](https://claudemarketplaces.com/)** — Daily-updated web aggregator tracking 6,700+ skills, 2,500+ marketplaces, and 840+ MCP servers. _The de facto discovery hub if you want to browse rather than `git clone`._
- **[Chat2AnyLLM/awesome-claude-plugins](https://github.com/Chat2AnyLLM/awesome-claude-plugins)** — Meta-list of 75+ marketplaces and ~1,200 plugins. _Use when you want to find a niche marketplace._
- **[claude-market/marketplace](https://github.com/claude-market/marketplace)** — Hand-curated open-source marketplace; small but quality-focused. _Worth contributing to if you want a high-signal home for your plugin._
- **[xiaolai/claude-plugin-marketplace](https://github.com/xiaolai/claude-plugin-marketplace)** — Actively maintained community marketplace. _Reasonable middle-ground between official and aggregator marketplaces._
- **[hekmon8/awesome-claude-code-plugins](https://github.com/hekmon8/awesome-claude-code-plugins)** — Curated list focused on day-to-day developer ergonomics. _Good for finding "vibe coding" workflow plugins._
- **[sgaunet/claude-plugins](https://github.com/sgaunet/claude-plugins)** — Three specialized bundles: devops-infrastructure, software-engineering, go-specialist. _Useful as a study of how to package a focused plugin pack._
- **[feed-mob/claude-code-marketplace](https://github.com/feed-mob/claude-code-marketplace)** — Vendor-style marketplace from the FeedMob dev team. _Example of a company publishing internal plugins externally._
- **[VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)** — 100+ specialized subagents. _Useful when you want pre-built sub-agents rather than full plugins._
- **[jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills)** — Cross-listed; bundles plugins + skills + agents with a CLI package manager. _The "everything store" option._

---

## Discovery hubs

When this catalog goes stale, these meta-resources will keep being current:

- **[claudemarketplaces.com](https://claudemarketplaces.com/)** — daily-updated aggregator (web UI).
- **[hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)** — most-watched community index.
- **[Anthropic's Claude Code docs](https://code.claude.com/docs/en/skills)** — official documentation on skills, hooks, and plugins.

---

## Caveats

- **Freshness:** Entries verified as of the snapshot date above. The plugin/skill space moves fast — repos can rename, stale, or fork. Click through before relying on anything.
- **Name collisions:** Several "awesome-claude-code" and "awesome-claude-skills" repos exist in different orgs. The ones listed above are the most established at time of writing.
- **Licenses:** Most repos lack explicit `LICENSE` files at root; GitHub defaults apply. If you redistribute code, check the actual license rather than assuming MIT.
- **Not an endorsement:** Listing here means a repo was discoverable and looked active, not that it was audited for code quality or security.
- **Atomic Agents specifically:** Beyond the official `atomic-forge`, expect to write your own tools rather than find community ones. The framework is solid, but the ecosystem is still young.
