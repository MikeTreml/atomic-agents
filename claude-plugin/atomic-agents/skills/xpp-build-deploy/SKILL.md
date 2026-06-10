---
name: xpp-build-deploy
description: Orchestrate D365 Finance & Operations (X++) build, database sync, model packaging, and deployment. Wraps the d365fo.tools PowerShell module (community, MIT) and Microsoft's official Dynamics365-Xpp-Samples-Tools Azure DevOps pipeline templates. Use when the user asks to "build the model", "sync the database", "package the deployable", "set up the D365 pipeline", "deploy to UAT", "wire up Azure DevOps for X++", or runs `/atomic-agents:xpp-build-deploy`.
---

# Build, Sync, Package, Deploy — D365 F&O

This skill is the action-oriented path for the *delivery* side of D365 F&O development: get a model compiled, the DB synced, a deployable package produced, and a CI pipeline scaffolded. It assumes the authoring is done.

The heavy lifting comes from two external projects we link to but do not vendor:

- **`d365fo.tools`** — community PowerShell module (MIT), ~50 cmdlets, mature. [GitHub](https://github.com/d365collaborative/d365fo.tools). Anything labelled "PowerShell cmdlet" below ships in this module.
- **`microsoft/Dynamics365-Xpp-Samples-Tools`** — Microsoft's official YAML pipeline samples. [GitHub](https://github.com/microsoft/Dynamics365-Xpp-Samples-Tools). The pipeline scaffolding sections paraphrase the `xpp-ci.yml` template there.

For ambient code context the model/AOT layout is in the sibling `xpp-authoring` skill's references; this skill stays focused on delivery.

## When this fires vs. xpp-authoring

- **This skill**: build / sync / package / pipeline / deploy questions.
- **`xpp-authoring`**: writing or wiring AOT objects.

If a request mixes both ("scaffold this class AND set up the pipeline"), do the authoring first, then come back here.

## Phase 1 — Confirm the runtime context

The build/deploy story differs sharply by environment. Confirm before doing anything:

1. **Tier-1 dev VM (cloud-hosted or local Hyper-V).** You have Visual Studio with the F&O dev tools and `d365fo.tools` installed. Full local build + sync available.
2. **Tier-2/3/UAT/Prod sandbox.** No build there. You produce a deployable package locally (or in CI) and apply it via LCS.
3. **Linux / Mac dev machine.** No local build at all. Use CI for builds; iterate on the dev VM for sync-required changes.

A common failure mode is trying to run dev-VM steps from a developer laptop and getting cryptic errors. **Verify which environment we're on before scripting anything.**

## Phase 2 — The five things you can do

### A. Build a model (local, dev VM)

PowerShell (uses `d365fo.tools`):

```powershell
Invoke-D365ModuleFullCompile -Module "MyExtensionModel"
```

Or the equivalent MSBuild route (what Visual Studio runs under the hood):

```cmd
msbuild "C:\AOSService\PackagesLocalDirectory\MyExtensionModel\MyExtensionModel.rnrproj" /t:Build /p:Configuration=Release
```

**Verify:** check the resulting `bin\Dynamics.AX.<Model>.dll` exists with a recent timestamp. The PowerShell cmdlet emits a summary; review for errors before moving on.

### B. Sync the database

```powershell
Invoke-D365DbSync -Module "MyExtensionModel" -Verbose
# Or full sync (slow, but safe after a Microsoft platform update):
Invoke-D365DbSync -SyncMode Full
```

Run after **any** table/index/EDT metadata change. Skipping this is the source of "I added a field but the form errors out" reports.

### C. Run Best Practice checks

```powershell
Invoke-D365XppBpAnalysis -Module "MyExtensionModel" -ShowResults
```

Under the hood this shells out to `xppbp.exe`. Pair with the `XppBpRunnerTool` Python wrapper (`atomic-forge/tools/xpp_bp_runner/`) if you want the results as structured data inside an agent pipeline.

### D. Produce a deployable package

```powershell
$pkg = New-D365DeployablePackage -Module "MyExtensionModel" `
    -PackageName "MyExtensionModel" `
    -Path "C:\Temp\packages\$(Get-Date -Format 'yyyyMMdd-HHmm').zip"
Write-Host "Package: $pkg"
```

This produces the zip you upload to LCS. **Keep the zip naming reproducible** — include the model name and a timestamp or commit SHA so it traces back to the source.

### E. Apply a package to a sandbox

Don't script direct deploy to UAT/Prod from a dev machine. Use **LCS** (Lifecycle Services) via the portal or via the LCS asset-library APIs in CI. Sample CI snippet:

```yaml
- task: AzureCLI@2
  displayName: 'Upload deployable package to LCS'
  inputs:
    azureSubscription: '<service-connection>'
    scriptType: 'pscore'
    scriptLocation: 'inlineScript'
    inlineScript: |
      Install-Module d365fo.tools -Force -Scope CurrentUser
      Invoke-D365InstallationPackage -path "$(Build.ArtifactStagingDirectory)/<package>.zip" -lcsAssetLibraryId "<id>"
```

(Adjust to your service connection / LCS project ID.)

## Phase 3 — Azure DevOps pipeline scaffolding

For a green-field pipeline, paraphrase Microsoft's `xpp-ci.yml` from `Dynamics365-Xpp-Samples-Tools`. The four jobs are:

1. **Setup** — install / cache `d365fo.tools`, restore NuGet packages used by the dev tools.
2. **Build** — `Invoke-D365ModuleFullCompile -Module "<YourModel>"`.
3. **BP analysis** — `Invoke-D365XppBpAnalysis -Module "<YourModel>" -ShowResults`. Fail the pipeline on Error-severity findings.
4. **Package** — `New-D365DeployablePackage` and publish as a build artifact.

Skeleton:

```yaml
trigger:
  branches:
    include: [ main ]

pool:
  vmImage: 'windows-latest'   # MUST be Windows; X++ tools don't run on Linux runners.

steps:
  - task: PowerShell@2
    displayName: 'Install d365fo.tools'
    inputs:
      targetType: 'inline'
      script: 'Install-Module -Name d365fo.tools -Force -Scope CurrentUser'

  - task: PowerShell@2
    displayName: 'Build module'
    inputs:
      targetType: 'inline'
      script: 'Invoke-D365ModuleFullCompile -Module "MyExtensionModel"'

  - task: PowerShell@2
    displayName: 'BP analysis'
    inputs:
      targetType: 'inline'
      script: |
        $findings = Invoke-D365XppBpAnalysis -Module "MyExtensionModel" -ShowResults
        if ($findings | Where-Object Severity -eq "Error") { exit 1 }

  - task: PowerShell@2
    displayName: 'Package'
    inputs:
      targetType: 'inline'
      script: |
        New-D365DeployablePackage -Module "MyExtensionModel" `
          -PackageName "MyExtensionModel" `
          -Path "$(Build.ArtifactStagingDirectory)\MyExtensionModel-$(Build.BuildNumber).zip"

  - task: PublishBuildArtifacts@1
    inputs:
      pathToPublish: '$(Build.ArtifactStagingDirectory)'
      artifactName: 'deployable'
```

**Pin the agent image to Windows.** X++ tooling is Windows-only. A Linux runner will silently waste minutes before failing.

## Phase 4 — Verify

After running anything that matters, confirm:

1. **Build:** `bin\Dynamics.AX.<Model>.dll` exists and was modified inside the last few minutes.
2. **DB sync:** open the affected form on the dev VM and confirm the new field/index appears.
3. **BP:** zero Error-severity findings on the changeset. Warnings are informational.
4. **Package:** the zip opens cleanly in Windows Explorer and shows the model folder inside.
5. **CI:** the published artifact downloads, is the right size (>0 bytes, sanity-check), and contains the expected files.

## Anti-patterns

- **Don't run `Invoke-D365DbSync -SyncMode Full` casually** — it's slow and only needed after platform updates. Module-scoped sync is the default for everyday work.
- **Don't deploy from a dev machine to UAT/Prod.** Go through LCS or CI — every time. The few minutes saved by skipping LCS will cost a weekend rolling back.
- **Don't pin a package zip path to a fixed name.** Including a timestamp or commit SHA makes incident-response one step shorter.
- **Don't run BP analysis only in CI.** Run it locally too — the feedback loop is much faster, and CI failures on style-only findings are infuriating.
- **Don't commit the dev-VM-specific paths** (e.g. `J:\AOSService\...`) into pipeline scripts. Parameterize via pipeline variables.

## References & community resources

- [d365collaborative/d365fo.tools](https://github.com/d365collaborative/d365fo.tools) — PowerShell module powering most steps above.
- [microsoft/Dynamics365-Xpp-Samples-Tools](https://github.com/microsoft/Dynamics365-Xpp-Samples-Tools) — official YAML pipeline templates.
- [dynamics365ninja/d365fo-mcp-server](https://github.com/dynamics365ninja/d365fo-mcp-server) — MCP server with build/metadata tooling, useful when you want Claude Code itself to introspect the build state.
- [ccampora/mcp_xpp](https://github.com/ccampora/mcp_xpp) — MCP server with VS2022 integration; alternative to the above.
- [Microsoft Learn — Build automation](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-tools/build-automation) — authoritative docs.
