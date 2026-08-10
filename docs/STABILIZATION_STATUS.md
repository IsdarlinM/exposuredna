# Exposure DNA 0.5.13 stabilization status

Date: 2026-08-10

Exposure DNA 0.5.13 is under Sentinel Forge P0/P1 stabilization and is not considered a fully gated stable release until the exact release commit passes coordinated Windows/Linux, Python 3.11-3.13, security and supply-chain gates.

This branch adds a data-preserving Windows uninstaller, removes CI private-token/branch coupling and adds uninstall regression coverage. Entity correlation remains conservative: similarity alone never validates organization ownership.

The official update channel remains unchanged until hosted CI can execute and dependency review, signed release, SBOM and provenance evidence are complete.
