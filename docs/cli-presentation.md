# CLI presentation

Exposure DNA 0.5.11 uses the shared Sentinel Forge CLI presentation contract from SRIC Core.

Interactive console sessions show a subdued green ASCII banner ordered as `Exposure DNA :: v0.5.11`, `Developer: IsdarlinM`, then the concise purpose statement. The banner is written to interactive stderr, keeping stdout suitable for JSON, graph exports, redirection, and automation.

Use `exposuredna --no-color COMMAND` to disable ANSI/Rich colors. The installed console entrypoint also normalizes `exposuredna COMMAND --no-color`. The standard `NO_COLOR` environment variable is honored.

Installer-internal doctor/capability/help smokes use `SENTINEL_BANNER=never` and a temporary diagnostic log so successful installs do not print the banner repeatedly; captured output is emitted only when validation fails.

The public help contract includes `exposuredna --help`, `exposuredna -h`, `exposuredna help`, `exposuredna COMMAND --help`, `exposuredna COMMAND -h`, and `exposuredna COMMAND help`. The release regression suite walks every public command and compares its ordered CLI parameters with the Web Feature Workbench schema.

Typer/Rich command and help presentation is colorized by default. `--no-color` changes presentation only; it does not alter organization relationships, evidence, temporal claims, update verification, Web Feature Workbench/Command Console behavior, CSP enforcement, or API responses.
