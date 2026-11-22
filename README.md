Claude, Copilot, Muse, and Grokbot open branches and pull requests. Work has two lanes, mapped in [.github/CODEOWNERS](.github/CODEOWNERS) and explained in [.github/lane/README.md](.github/lane/README.md):

- **Agent lane:** a pull request that touches only the rehearsal loop's own work (its backlog, its score ledger, the synthetic year and engine) merges itself once every required check passes.
- **Owner's lane:** everything else, including every check, the goal file, the lane map, workflows and rulesets, waits for the repository owner, who alone merges it.

The `main` branch is protected by the `main: history` and `main: owner merges` rulesets.
