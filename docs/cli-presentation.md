# CLI presentation

Exposure DNA 0.5.2 uses the shared Sentinel Forge CLI presentation contract from SRIC Core.

Interactive console sessions show a subdued green ASCII banner with the product name, a one-line purpose statement, and `IsdarlinM :: v0.5.2`. The banner is written to interactive stderr, keeping stdout suitable for JSON, graph exports, redirection, and automation.

Use `exposuredna --no-color COMMAND` to disable ANSI/Rich colors. The installed console entrypoint also normalizes `exposuredna COMMAND --no-color`. The standard `NO_COLOR` environment variable is honored.

Typer/Rich command and help presentation is colorized by default. `--no-color` changes presentation only; it does not alter organization relationships, evidence, temporal claims, or API responses.
