# Community Catalog

A curated list of community-built **skills**, **atomic-agents tools**, and **plugin bundles** you can pull from when building with Atomic Agents and Claude Code.

This is a **discovery aid**, not vendored code. Links lead to upstream repos — check each project's license before copying anything into your own codebase. Inclusion here is not an endorsement.

> Snapshot date: 2026-05-26. The Claude Code ecosystem moves fast; expect this list to drift. For a fresher, programmatic feed see `scripts/gather_community_catalog.py` (it writes `community-catalog.json` from the GitHub API).

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

The Claude Code skills ecosystem is dense and active. Below is a curated cross-section by domain.

### Foundational

- **[anthropics/skills](https://github.com/anthropics/skills)** — Anthropic's official public examples. _The canonical reference for SKILL.md structure._
- **[hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)** — The largest single curated index. _Best entry point if you don't know what you're looking for yet._
- **[VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)** — 1,000+ agent skills across domains. _Broadest list currently published._

### Multi-purpose collections

- **[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)** — 300+ production-ready skills by role (Engineering, Product, Research, etc.). _When you want a role-shaped skill._
- **[travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)** — Curated list focused on workflow customization. _Good secondary index._
- **[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)** — Skills focused on workflow customization. _Useful for integration-heavy use cases._
- **[daymade/claude-code-skills](https://github.com/daymade/claude-code-skills)** — Skills + bundled MCP server pattern. _Study example for MCP-integrated skills._
- **[obviousworks/Claude-AI-skills-collection-2026](https://github.com/obviousworks/Claude-AI-skills-collection-2026)** — Curated collection with clear submission guidelines. _Worth watching for new additions._
- **[affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)** — Hackathon-built collection (performance, memory, security, research). _Useful for skill composition patterns._
- **[jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills)** — 2,800+ skills aggregation with `ccpi` CLI installer. _Use when you want a marketplace experience._

### DevOps & infrastructure

- **[ahmedasmar/devops-claude-skills](https://github.com/ahmedasmar/devops-claude-skills)** — DevOps skill marketplace covering K8s, CI/CD, monitoring, FinOps. _For cloud automation workflows._
- **[LukasNiessen/kubernetes-skill](https://github.com/LukasNiessen/kubernetes-skill)** — Kubernetes expertise with KubeShark integration. _For production-grade K8s manifests._
- **[akin-ozer/cc-devops-skills](https://github.com/akin-ozer/cc-devops-skills)** — Terraform, Helm, Checkov DevOps pack. _For IaC workflows and policy checks._
- **[zxkane/aws-skills](https://github.com/zxkane/aws-skills)** — AWS CDK, serverless, cost-ops skills with MCP integration. _For AWS-native builds._
- **[IncomeStreamSurfer/claude-aws-toolkit](https://github.com/IncomeStreamSurfer/claude-aws-toolkit)** — AWS infrastructure management with best practices. _For AWS deployments._
- **[a-pavithraa/aws-serverless-skill](https://github.com/a-pavithraa/aws-serverless-skill)** — AWS serverless + Terraform patterns. _For Lambda/DynamoDB multi-env setups._
- **[lgbarn/devops-skills](https://github.com/lgbarn/devops-skills)** — Terraform/OpenTofu with safety-first IaC. _For IaC governance._
- **[suwa-sh/multi-cloud-lifecycle-skills](https://github.com/suwa-sh/multi-cloud-lifecycle-skills)** — AWS/Azure/GCP vendor-neutral architecture. _For multi-cloud designs._
- **[mongodb/agent-skills](https://github.com/mongodb/agent-skills)** — Official MongoDB agent skills. _For MongoDB development and ops._

### Security & pentesting

- **[Masriyan/Claude-Code-CyberSecurity-Skill](https://github.com/Masriyan/Claude-Code-CyberSecurity-Skill)** — 15 cybersecurity skills (offensive, SOC, threat hunting). _Solid vertical skill pack._
- **[Eyadkelleh/awesome-claude-skills-security](https://github.com/Eyadkelleh/awesome-claude-skills-security)** — SecLists wordlists + pentest agents. _For authorized security assessments._
- **[transilienceai/communitytools](https://github.com/transilienceai/communitytools)** — 26 security skills covering the full pentest lifecycle. _For comprehensive bug bounties._
- **[frendysanusi/claude-pentest-skills](https://github.com/frendysanusi/claude-pentest-skills)** — Web app pentesting structured by OWASP methodology. _For methodical app sec assessments._
- **[trilwu/secskills](https://github.com/trilwu/secskills)** — 16 security skills + 6 subagent security experts. _For deep cross-domain security analysis._
- **[mahmutka/cybersecurity-claude-skills](https://github.com/mahmutka/cybersecurity-claude-skills)** — Web hacking, recon, secure code review, CTF. _For offensive security and code analysis._
- **[Stickman230/claude-pentest](https://github.com/Stickman230/claude-pentest)** — Pentesting framework: 15 agents, 63 attack categories. _For end-to-end pentest workflows._
- **[trailofbits/skills](https://github.com/trailofbits/skills)** — Trail of Bits security research and audit workflows. _When auditing for vulns._
- **[shuvonsec/web3-bug-bounty-hunting-ai-skills](https://github.com/shuvonsec/web3-bug-bounty-hunting-ai-skills)** — 18 smart contract security skills from 2,749 Immunefi reports. _For Web3 security research._

### Finance & trading

- **[JoelLewis/finance_skills](https://github.com/JoelLewis/finance_skills)** — 81 financial-services skills (investment, trading, compliance). _For quantitative and institutional finance._
- **[agiprolabs/claude-trading-skills](https://github.com/agiprolabs/claude-trading-skills)** — 62 trading/DeFi/quant skills with multi-step workflows. _For algo trading and quant analysis._
- **[tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills)** — Market analysis, charting, economic calendars. _For trading strategy development._
- **[javajack/skill-algotrader](https://github.com/javajack/skill-algotrader)** — Quantitative trading with Zerodha for Indian markets. _For live algorithmic trading._
- **[quant-sentiment-ai/claude-equity-research](https://github.com/quant-sentiment-ai/claude-equity-research)** — Institutional-grade equity research with fundamental + technical analysis. _For professional investment research._

### Academic research & writing

- **[Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills)** — Research pipeline (research → write → review → finalize). _When writing research papers._
- **[flonat/claude-research](https://github.com/flonat/claude-research)** — PhD-focused research infrastructure with skills + hooks. _For academic/thesis workflows._
- **[lishix520/academic-paper-skills](https://github.com/lishix520/academic-paper-skills)** — Planning + writing academic papers with quality checkpoints. _For systematic paper composition._
- **[fcakyon/phd-skills](https://github.com/fcakyon/phd-skills)** — PhD reproduction, experiment design, review skills. _For reproducible research validation._
- **[Galaxy-Dawn/claude-scholar](https://github.com/Galaxy-Dawn/claude-scholar)** — Semi-automated research assistant: ideation → publication. _For end-to-end research workflows._

### Testing & QA

- **[lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill)** — Browser automation with Playwright (model-invoked). _For auto-generated E2E tests._
- **[yusuftayman/playwright-cli-agents](https://github.com/yusuftayman/playwright-cli-agents)** — E2E test generation + debugging with Page Object Model. _For QA automation pipelines._
- **[neonwatty/qa-skills](https://github.com/neonwatty/qa-skills)** — QA automation, mobile audits, 6 specialized agents. _For comprehensive test coverage._
- **[agentmantis/test-skills](https://github.com/agentmantis/test-skills)** — Production-grade Playwright tests with POM. _For SDET-level test frameworks._

### Media (video, asset, design)

- **[6missedcalls/video-editing-skill](https://github.com/6missedcalls/video-editing-skill)** — Trim, captions, overlays (Bash + FFmpeg + Whisper). _For automating video production._
- **[digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit)** — AI-native video production toolkit. _When editing videos programmatically._
- **[alonw0/web-asset-generator](https://github.com/alonw0/web-asset-generator)** — Auto-generate favicons, app icons, social images. _For asset pipelines._
- **[neonwatty/logo-designer-skill](https://github.com/neonwatty/logo-designer-skill)** — Iterative SVG logo design. _For procedural logo generation._
- **[zephyrwang6/brand-design-md](https://github.com/zephyrwang6/brand-design-md)** — Design language from 62 world-class brands. _For brand-consistent design._
- **[nafiurrahmanniloy/figma-skill](https://github.com/nafiurrahmanniloy/figma-skill)** — Universal Figma-to-code for 7 frameworks. _For translating designs to production code._
- **[phazurlabs/ux-ui-mastery](https://github.com/phazurlabs/ux-ui-mastery)** — 19 skills + 55 references for UI/UX. _For professional design workflows._

### Legal & compliance

- **[evolsb/claude-legal-skill](https://github.com/evolsb/claude-legal-skill)** — Contract review with CUAD risk detection + market benchmarks. _For first-pass contract analysis._
- **[zubair-trabzada/ai-legal-claude](https://github.com/zubair-trabzada/ai-legal-claude)** — Contract review, risk analysis, NDA generation, compliance auditing. _For legal document workflows._
- **[anthropics/claude-for-legal](https://github.com/anthropics/claude-for-legal)** — Official Anthropic legal workflows with tracked changes. _For legal teams using Word integration._
- **[Sushegaad/Claude-Skills-Governance-Risk-and-Compliance](https://github.com/Sushegaad/Claude-Skills-Governance-Risk-and-Compliance)** — ISO 27001, SOC 2, FedRAMP, GDPR, HIPAA, NIST CSF. _For GRC frameworks and audits._

### Project & product management

- **[automazeio/ccpm](https://github.com/automazeio/ccpm)** — Project management using GitHub Issues with parallel agent execution. _For distributed team orchestration._
- **[phuryn/pm-skills](https://github.com/phuryn/pm-skills)** — 100+ PM skills from discovery to strategy, execution, growth. _For guiding product development._
- **[DarrenJCoxon/agile-studio](https://github.com/DarrenJCoxon/agile-studio)** — Specialist team (BA, PM, UX, Architect, PO) as a single skill. _For role-specialized agile delivery._

---

## Category B — Atomic Agents Tools (`BaseTool` subclasses)

The community ecosystem beyond the official forge is genuinely thin. This repo's local forge now includes a small **filesystem & binary-analysis pack** added on top of the upstream toolset.

### In-repo forge tools (this fork)

- **[`atomic-forge/tools/file_search`](../../atomic-forge/tools/file_search/)** — Recursive filesystem search by filename glob and/or content regex. Pure stdlib. _Use when an agent needs to locate code, configs, or logs without leaving the pipeline._
- **[`atomic-forge/tools/pe_inspector`](../../atomic-forge/tools/pe_inspector/)** — Static PE inspection (`.exe`/`.dll`/`.sys`): headers, imports, exports, sections, SHA-256. Uses `pefile`. _For reverse engineering, malware triage, or learning what a DLL exposes — without executing it._
- **[`atomic-forge/tools/dll_research`](../../atomic-forge/tools/dll_research/)** — Lookup of what 30+ common Windows DLLs do (kernel32, user32, ntdll, ws2_32, crypt32, ...). Self-contained reference table; unknown DLLs return a Microsoft Learn search URL. _Chains naturally after `pe_inspector` to explain each imported DLL._

These three chain together: `file_search` → find candidate binaries → `pe_inspector` → extract imported DLLs → `dll_research` → explain what each one provides.

### Official + community

- **[BrainBlend-AI/atomic-agents/atomic-forge](https://github.com/BrainBlend-AI/atomic-agents/tree/main/atomic-forge)** — Upstream tool collection: calculator, web search (SearXNG, Tavily), PDF reader, Wikipedia, YouTube transcript, weather, arXiv, more. _Check here first before building your own._
- **[atomic-forge tool structure guide](../../atomic-forge/guides/tool_structure.md)** — Local guide on tool layout and conventions. _Read this before writing your own tool._
- **[w3bwizart/Atomic_Agents_Learn](https://github.com/w3bwizart/Atomic_Agents_Learn)** — Learning repo with custom agent + tool examples. _Useful for seeing third-party structure._
- **[mrseanryan/gpt-multi-atomic-agents](https://github.com/mrseanryan/gpt-multi-atomic-agents)** — Multi-agent framework built on `atomic_agents` + Instructor + Pydantic. _Not a tool itself; closest third-party framework extension._
- **[bububa/atomic-agents](https://github.com/bububa/atomic-agents)** — A Go re-implementation. _Reference if you want the design pattern in another language._

> **Contribution opportunities.** There's no community `awesome-atomic-agents` list, and remaining gaps include: a Reddit search tool, a Slack message tool, a GitHub-issues tool, a Notion tool, a generic SQL-query tool, a strings extractor (mimicking the Unix `strings` command), and a decompiler-runner wrapping Ghidra/IDA/dnSpy headlessly. If you build one, link it back here.

---

## Category C — Plugin Marketplaces & Bundles

Plugin marketplaces ship bundles of skills + agents + commands together, installable via Claude Code's `/plugin` command. The `.claude-plugin/plugin.json` manifest format stabilized in late 2025.

### Foundational

- **[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)** — Anthropic-managed directory of reviewed plugins. _Start here; highest quality bar._
- **[claudemarketplaces.com](https://claudemarketplaces.com/)** — Daily-updated web aggregator (6,700+ skills, 2,500+ marketplaces, 840+ MCP servers). _De facto discovery hub._

### Multi-plugin marketplaces (general)

- **[Chat2AnyLLM/awesome-claude-plugins](https://github.com/Chat2AnyLLM/awesome-claude-plugins)** — Meta-list of 75+ marketplaces and ~1,200 plugins. _When looking for a niche marketplace._
- **[ComposioHQ/awesome-claude-plugins](https://github.com/ComposioHQ/awesome-claude-plugins)** — 500+ app integrations + AgentLint, code-review, test-writer, mcp-builder. _When you need broad SaaS integrations._
- **[GiladShoham/awesome-claude-plugins](https://github.com/GiladShoham/awesome-claude-plugins)** — Plugin marketplace with CI validation and contributor guidelines. _For higher signal-to-noise picks._
- **[rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit)** — 135+ agents, 35 skills, 42 commands, 176+ plugins, 20 hooks. _Largest single toolkit._
- **[jmanhype/awesome-claude-code](https://github.com/jmanhype/awesome-claude-code)** — Tracks plugins, MCP servers, editor integrations, ecosystem. _Good ecosystem overview._
- **[ccplugins/awesome-claude-code-plugins](https://github.com/ccplugins/awesome-claude-code-plugins)** — Slash commands, subagents, MCP servers, hooks by domain. _For domain-organized discovery._
- **[claude-market/marketplace](https://github.com/claude-market/marketplace)** — Hand-curated open-source marketplace. _Quality-focused, smaller, contribution-friendly._
- **[xiaolai/claude-plugin-marketplace](https://github.com/xiaolai/claude-plugin-marketplace)** — Actively maintained community marketplace. _Middle ground between official and aggregator._
- **[hekmon8/awesome-claude-code-plugins](https://github.com/hekmon8/awesome-claude-code-plugins)** — Day-to-day developer ergonomics. _For "vibe coding" workflow plugins._
- **[sgaunet/claude-plugins](https://github.com/sgaunet/claude-plugins)** — Three specialized bundles: devops-infra, software-engineering, go-specialist. _Study of focused plugin pack design._
- **[quemsah/awesome-claude-plugins](https://github.com/quemsah/awesome-claude-plugins)** — Automated adoption-metrics collection via n8n. _For data on what's actually used._
- **[AwesomeJun/awesome-claude-plugins](https://github.com/AwesomeJun/awesome-claude-plugins)** — Plugin marketplace featuring design plugins. _For visually polished plugins._
- **[huangdijia/oh-my-claude-code-plugins](https://github.com/huangdijia/oh-my-claude-code-plugins)** — Shell-inspired organization. _If you like oh-my-zsh aesthetics._
- **[PayRequest/claude-plugins](https://github.com/PayRequest/claude-plugins)** — Plugins for Claude Code development workflows. _General productivity._
- **[Dev-GOM/claude-code-marketplace](https://github.com/Dev-GOM/claude-code-marketplace)** — Developer-focused hooks, commands, agents. _For workflow automation._
- **[feed-mob/claude-code-marketplace](https://github.com/feed-mob/claude-code-marketplace)** — Vendor-style marketplace from FeedMob dev team. _Example of a company publishing internal plugins._
- **[jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills)** — Bundles plugins + skills + agents with a CLI package manager. _The "everything store" option._
- **[VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)** — 100+ specialized subagents. _When you want pre-built subagents._

### Security & DevOps

- **[harish-garg/security-scanner-plugin](https://github.com/harish-garg/security-scanner-plugin)** — Vuln scanning with GitHub data + AI explanations and fixes. _For automated code-security review._
- **[efij/awesome-claude-code-security](https://github.com/efij/awesome-claude-code-security)** — Hardening tools, threat research, governance frameworks. _For security-focused workflows._
- **[kubestellar/claude-plugins](https://github.com/kubestellar/claude-plugins)** — Multi-cluster Kubernetes ops. _For managing many K8s clusters._
- **[Sagart-cactus/claude-k8s-plugin](https://github.com/Sagart-cactus/claude-k8s-plugin)** — Kubernetes CRD operators with Tilt fast dev loop. _For K8s operator development._

### Data science & analytics

- **[Data-Wise/claude-plugins](https://github.com/Data-Wise/claude-plugins)** — 13 slash commands + 17 A-grade skills for R. _For statistical research in R._
- **[ai-analyst-lab/ai-analyst](https://github.com/ai-analyst-lab/ai-analyst)** — 18-agent pipeline for data analysis + slide deck generation. _For automated analyst reports._
- **[danielrosehill/Claude-Data-Visualisation-And-Publishing-Plugin](https://github.com/danielrosehill/Claude-Data-Visualisation-And-Publishing-Plugin)** — Matplotlib, Bokeh, Chart.js, ECharts, D3 with smart tool selection. _For data viz pipelines._
- **[HungHsunHan/claude-code-data-science-team](https://github.com/HungHsunHan/claude-code-data-science-team)** — Multi-agent data science team simulation. _For end-to-end DS workflows._
- **[adityawrk/analytics-with-claude-code](https://github.com/adityawrk/analytics-with-claude-code)** — Skills, agents, hooks, workflows for data analysts/engineers. _For production analytics work._
- **[richard-gyiko/data-wrangler-plugin](https://github.com/richard-gyiko/data-wrangler-plugin)** — SQL analytics over CSV, Parquet, JSON, Excel via DuckDB. _For fast local data wrangling._

### Finance & trading

- **[coinpaprika/claude-marketplace](https://github.com/coinpaprika/claude-marketplace)** — Crypto market data + DeFi analytics (29 CEX + 14 DeFi MCP tools). _For crypto research._
- **[anthropics/financial-services](https://github.com/anthropics/financial-services)** — Official Anthropic financial-services reference agents + connectors. _Canonical FS starting point._

### Frontend & UI/UX

- **[wilwaldon/Claude-Code-Frontend-Design-Toolkit](https://github.com/wilwaldon/Claude-Code-Frontend-Design-Toolkit)** — Skills, plugins, MCP servers for better frontends. _For prettier frontend output._
- **[hemangjoshi37a/claude-code-frontend-dev](https://github.com/hemangjoshi37a/claude-code-frontend-dev)** — Multimodal visual testing with browser automation + vision-based UI validation. _For visual regression testing._
- **[HermeticOrmus/LibreUIUX-Claude-Code](https://github.com/HermeticOrmus/LibreUIUX-Claude-Code)** — 152 agents, 70 plugins, 76 commands for UI/UX. _Largest UI/UX system._
- **[claudekit/frontend-design-pro-demo](https://github.com/claudekit/frontend-design-pro-demo)** — 11 design aesthetics (minimalism, neumorphism, glassmorphism, brutalism). _For exploring design directions._
- **[Koomook/claude-frontend-skills](https://github.com/Koomook/claude-frontend-skills)** — Distinctive, non-generic frontend designs. _For escaping "AI slop" UI._

### Writing & documentation

- **[danielrosehill/writing-editing-plugin](https://github.com/danielrosehill/writing-editing-plugin)** — Proofreading, style editing, text transformation. _For writing workflows._
- **[matsengrp/plugins](https://github.com/matsengrp/plugins)** — Scientific writing, code review, technical docs. _For academic writing pipelines._

### Game development

- **[Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)** — 49 AI agents + 72 workflow skills + studio hierarchy. _Full game-dev studio simulation._
- **[hiddenpeopleclub/claude-code-plugins](https://github.com/hiddenpeopleclub/claude-code-plugins)** — C++ game dev: 9 agents (review, style, perf, security). _For C++ game projects._
- **[sponticelli/gamedev-claude-plugins](https://github.com/sponticelli/gamedev-claude-plugins)** — Game-dev plugin collection. _For Unity/Unreal-style workflows._

### Language-specific & LSP

- **[Piebald-AI/claude-code-lsps](https://github.com/Piebald-AI/claude-code-lsps)** — LSPs for 20+ languages (Rust, Go, TypeScript, Python, Kotlin). _For language-aware tooling._

### Mobile, Docker, remote

- **[AlexGladkov/claude-in-mobile](https://github.com/AlexGladkov/claude-in-mobile)** — Mobile automation: Android (ADB), iOS Simulator (simctl), Desktop (Compose). _For mobile dev workflows._
- **[docker/claude-plugins](https://github.com/docker/claude-plugins)** — Official Docker plugins integrating Docker Desktop's MCP Toolkit. _For container workflows._
- **[danielrosehill/docker-asist-plugin](https://github.com/danielrosehill/docker-asist-plugin)** — Container management, containerization, troubleshooting. _For Dockerfile/Compose work._
- **[siteboon/claudecodeui](https://github.com/siteboon/claudecodeui)** — Web UI for remote Claude Code session management on mobile/desktop. _For working from a phone._

### Database

- **[rdimascio/supabase-marketplace](https://github.com/rdimascio/supabase-marketplace)** — Supabase plugins for database, auth, storage, realtime, edge functions. _For full-stack Supabase apps._

---

## Discovery hubs

When this catalog goes stale, these meta-resources will keep being current:

- **[claudemarketplaces.com](https://claudemarketplaces.com/)** — daily-updated aggregator (web UI).
- **[VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)** — 1,000+ entries, currently the broadest list.
- **[hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)** — most-watched community index.
- **[github.com/topics/claude-code-plugin](https://github.com/topics/claude-code-plugin)** — 2,650+ tagged repos.
- **[github.com/topics/claude-code-skill](https://github.com/topics/claude-code-skill)** — skill-tagged repos.
- **[Anthropic's Claude Code docs](https://code.claude.com/docs/en/skills)** — official docs on skills, hooks, plugins.

## Auto-refresh

The markdown above is hand-curated, but there's a companion programmatic feed at `scripts/gather_community_catalog.py`. Run it locally or in CI to produce `community-catalog.json` — a machine-readable index pulled from GitHub's search API (topics + readme signals) that you can diff over time or use to surface new candidates for hand-curation.

```bash
GITHUB_TOKEN=ghp_xxx python scripts/gather_community_catalog.py
# → docs/guides/community-catalog.json
```

The script needs `api.github.com` reachable — many cloud sandboxes block it, so run locally.

---

## Caveats

- **Freshness:** Snapshot date at the top. The plugin/skill space moves fast — repos rename, stale, or fork. Click through before relying on anything.
- **Name collisions:** Many "awesome-claude-*" repos exist across different orgs. Star counts and recent commits are the best disambiguators.
- **Licenses:** Most repos lack explicit `LICENSE` files at root; GitHub defaults apply. If you redistribute code, check the actual license rather than assuming MIT.
- **Not an endorsement:** Listing here means a repo was discoverable and looked active, not that it was audited for code quality or security. **Especially for security-tooling and pentest skill packs** — review before running them against any system you don't own.
- **Atomic Agents specifically:** Beyond the official `atomic-forge`, expect to write your own tools rather than find community ones. The framework is solid, but the ecosystem is still young.
