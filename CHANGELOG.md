# Changelog

All notable changes to the **Gamelate CLI–Wrapper Protocol (GCWP)** are
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
for the **protocol version** (MAJOR.MINOR), not for the specification document.

---

## [1.0] — 2026-09-09 — Draft

### Added

- Initial release of the GCWP specification set, split from the monolithic
  protocol document previously appended to
  [`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents).
- Repository rename: `gamelate` → `gallate` (per author decision).
  The protocol short-name `GCWP` and the term `Gamelate` are retained as
  historical anchors.

#### Documents (`docs/protocol/`)

- `00-glossary.md` — unified terminology
- `01-architecture.md` — three-layer architecture (OmegaT / Wrapper / CLI)
- `02-core-protocol.md` — wire protocol (YAML Line Protocol over stdin/stdout)
- `03-discovery.md` — manifest + features capability discovery
- `04-operations.md` — operation request, input/output, ignore, options
- `05-events.md` — event stream (started / progress / file / completed / …)
- `06-status.md` — runtime status (state / phase / current / progress)
- `07-statistics.md` — result statistics (files / text / images / …)
- `08-validation.md` — engine-specific validation rules (regex / placeholder / constraint)
- `09-diagnostics.md` — stderr stream and error code semantics
- `10-configuration.md` — `gallate.yaml` ↔ GCWP request translation
- `11-process.md` — process lifecycle (start / run / cancel / exit)
- `12-compatibility.md` — version negotiation, unknown fields, forward compat
- `13-conformance.md` — three conformance tiers (Basic / Standard / Full)
- `zh-CN/` — Chinese translations of every above document

#### Schemas (`schema/`)

- `gcwp.schema.json` — root schema (aggregates via `$ref`)
- `manifest.schema.json`
- `features.schema.json`
- `request.schema.json`
- `response.schema.json`
- `event.schema.json`
- `status.schema.json`
- `statistics.schema.json`
- `validation.schema.json`
- `cancel-command.schema.json`

#### Examples (`examples/`)

- `minimal-cli/` — Basic-tier worked example (3 files)
- `full-cli/` — Full-tier worked example (7 files)

### Changed

- Communication carrier: **JSONL → YAML Line Protocol**.
  Every line is an independent YAML document, recommended in
  flow-mapping single-line form (e.g. `{type: event, event: progress, …}`).
- CLI machine-mode flag: `--json` → `--yaml`.
- The protocol is now a separate repository rather than an Appendix
  inside `Documents/通用行为规范.txt`.

### Notes

- Status is **Draft**. Breaking changes to the on-disk schema before 1.0
  are allowed; field name changes that affect the wire format will be
  documented here.

---

## Pre-1.0 history

Prior to 1.0 the protocol existed as `Appendix A` of
`Documents/通用行为规范.txt` (versions 0.x). That document is now retired;
CLI authors must follow the schemas in this repository.