# Shell Layer Specification

**[English](./README.md) | [简体中文](./zh-CN/README.md)**

> ⚠️ **DRAFT — breaking changes possible.**
> Field names, schema shapes, and grammar MAY change without notice
> until the 1.0 release. Pin to a commit hash, not a version, when
> depending on this specification.

This directory defines the **Shell / Project-Config Layer** of the
gallate specification set. It covers everything that lives between the
user's shell and a gallate CLI process:

```text
Shell invocation
   ↓
gallate.yaml         (project-level config)
   ↓
Engine extensions    (per-engine options and Media sub-options)
   ↓
Output location
```

The companion **Protocol Layer** (IPC between Wrapper and CLI) lives at
[`../protocol/`](../protocol/) and is named **GCWP**. The two layers
fit together as follows:

```text
User shell  ─────────────────────▶  gallate.yaml  ─────┐
   │                                                  │
   │                                                  ▼
   ▼                                            Wrapper
gallate CLI                                           │
   │                                                  │
   │  ...same process, same invocation...             │
   │                                                  │
   │                                          GCWP request
   │                                                  │
   ▼                                                  ▼
stdout/stderr / exit                         stdin/stdout (YAML)
   │                                                  │
   ▼                                                  ▼
User                                          gallate CLI (as a
                                               process the Wrapper
                                               drives)
```

A single gallate CLI implements **both** the Shell-layer behavior
described here and the GCWP behavior in `../protocol/`. The Shell layer
is what the user invokes directly; the GCWP layer is what a Wrapper
(e.g. an OmegaT plugin) drives when embedding the CLI.

---

## Document index

| # | Document | Scope |
| --- | --- | --- |
| 00 | [Glossary](./00-glossary.md) | Unified terminology for the Shell layer |
| 01 | [Overview](./01-overview.md) | Design principles: Engine Specific, Project-Centric, Unix |
| 02 | [CLI Grammar](./02-cli-grammar.md) | `tool [op][media] project [options]` |
| 03 | [Operations](./03-operations.md) | `-e` extract / `-i` inject and media combinations |
| 04 | [Media](./04-media.md) | Standard media + engine-extension media + Sub-Media |
| 05 | [Config File](./05-config-file.md) | `gallate.yaml` complete schema |
| 06 | [Project Structure](./06-project-structure.md) | Standard init structure + engine-extension dirs |
| 07 | [Init](./07-init.md) | The `init` subcommand |
| 08 | [Engine Extensions](./08-engine-extensions.md) | `--engine.*`, sub-media includes/excludes |
| 09 | [Standard Flags](./09-std-flags.md) | `--output`, `--ignore`, `--dry-run`, `-v`, `-q`, `--force` |
| 10 | [Standard Output & Exit Codes](./10-stdout-stderr.md) | stdout vs stderr, exit code table |
| 11 | [Conformance](./11-conformance.md) | What "compatible with Shell layer" means |
| 12 | [File Structure](./12-file-structure.md) | What lives inside `text/`, `image/`, etc. |

Chinese translations: [`zh-CN/`](./zh-CN/)

Examples: [`../../shell-layer-examples/`](../../shell-layer-examples/)

---

## Status

Draft. See `../../README.md` for project-wide status; this directory
follows the same draft cycle.

## Relationship to GCWP

The Shell layer talks about **what the user types** and **what
appears in `gallate.yaml`**. The Protocol layer talks about **what
runs over stdin/stdout when a Wrapper drives the CLI**. CLI
implementations implement both. See
[`../protocol/10-configuration.md`](../protocol/10-configuration.md)
for how the Wrapper translates `gallate.yaml` into a GCWP request.