# 00. Glossary

> Status: **Normative**. Terms used throughout the Shell-layer spec.
> Cross-references the
> [Protocol-layer glossary](../protocol/00-glossary.md).

## A

### Argument

A single flag (e.g. `--output`) or key/value (e.g. `--ignore "*.tmp"`)
passed on the command line. Distinct from **Option** (a structured
key in `gallate.yaml`).

## C

### CLI (gallate CLI)

An executable that targets **one** specific game engine, engine
family, or resource format. Speaks both the Shell layer (this spec)
and the [Protocol layer (GCWP)](../protocol/00-glossary.md#c).

### CLI Override

A CLI argument that changes the value of a `gallate.yaml` field for
the current invocation without persisting the change.

### Config File

`gallate.yaml` — the project-level YAML file at the Project Root. See
[05-config-file.md](./05-config-file.md).

### Conformance

Whether a CLI complies with this spec. See
[11-conformance.md](./11-conformance.md).

### Configuration Priority

The order in which CLI / YAML / engine defaults are merged. See
[01-overview.md § Configuration vs Operation](./01-overview.md).

## D

### Default Media

The media list used when `-e` / `-i` are given without media flags.
Source: `media:` in `gallate.yaml`, or the engine default if absent.

### Dry Run

`--dry-run` — runs the operation logic up to (but not including)
actual resource mutation, then reports what would have happened. See
[09-std-flags.md § Dry Run](./09-std-flags.md#dry-run).

## E

### Engine Default

The fallback value a CLI uses when neither CLI nor YAML provides one.
Engine-specific; not standardized.

### Engine Extension

Any feature a CLI adds beyond the standard Shell layer. Must use the
`--engine.*` namespace. See
[08-engine-extensions.md](./08-engine-extensions.md).

### Extract

`-e` — read engine resources, produce translation assets. See
[03-operations.md § Extract](./03-operations.md#extract).

## F

### Force

`--force` — override safety checks (currently: allow `init` to
overwrite an existing project). See
[07-init.md § Force](./07-init.md#force).

## G

### gallate.yaml

The single project-level configuration file. Standard Project Target.
Schema: [05-config-file.md](./05-config-file.md).

## I

### Ignore

Glob patterns that exclude resources from any operation. See
[09-std-flags.md § Ignore](./09-std-flags.md#ignore).

### In-Place

Operation result replaces input. Standard CLI MUST NOT silently turn an
operation into in-place; the engine declares opt-in. See
[10-stdout-stderr.md § In-Place](./10-stdout-stderr.md#in-place).

### Inject

`-i` — read translated assets, produce engine output. See
[03-operations.md § Inject](./03-operations.md#inject).

### Init

`init` — project initialization subcommand. See
[07-init.md](./07-init.md).

## M

### Media

The resource type an operation targets. The **standard** set is just
two: `text` and `image`. `audio`, `video`, `font`, and any other
class are **engine-extension** media declared per engine. See
[04-media.md](./04-media.md).

### Media Sub-Option

Sub-categorization under a Media type, declared by the engine. E.g.
`text.hardcoded`, `image.portrait_diff`. See
[04-media.md § Sub-Media](./04-media.md#sub-media).

## O

### Operation

`-e` (extract) or `-i` (inject). The verb part of the CLI invocation.
See [03-operations.md](./03-operations.md).

### Option

A key in `gallate.yaml`. Two scopes:
- **Standard options**: `input`, `output`, `media`, `ignore`,
  `scripts`, `engine`.
- **Engine options**: keys under `engine:`, opaque to standard CLI.

### Output

The destination of an operation's result. See
[09-std-flags.md § Output](./09-std-flags.md#output).

## P

### Path Resolution

Relative paths are resolved against the Project Root (the directory
containing `gallate.yaml`), not the shell's current working directory.

### Pre / Post Script

User-provided scripts that run before and after the engine operation.
See [09-std-flags.md § Scripts](./09-std-flags.md#scripts) — actually
configured under `scripts:` in `gallate.yaml`, see
[05-config-file.md § scripts](./05-config-file.md#scripts).

### Project Root

The directory containing `gallate.yaml`. The anchor for all relative
paths.

## Q

### Quick Reference

The Shell layer grammar in one line: `tool [op][media] project
[options]`. See [02-cli-grammar.md](./02-cli-grammar.md).

## R

### Request ID (Protocol layer)

Distinct from this layer. See
[Protocol glossary § Operation ID](../protocol/00-glossary.md#i).

## S

### Script

Executable file invoked as a pre or post hook. Owned by the user;
galled via `scripts.pre` / `scripts.post` in `gallate.yaml`.

### Standard Output (stdout)

Operation result. The Wrapper MAY use it for machine-readable output.
NOT for human progress.

### Standard Error (stderr)

Progress, warnings, diagnostics. Free-form, NOT parsed by Wrapper.

### Sub-Media

Engine-defined children of a Media type. See
[04-media.md § Sub-Media](./04-media.md#sub-media).

## T

### Tool

The gallate CLI executable. Generic name used throughout this spec.

## U

### Unknown Media

A media identifier the engine doesn't support. CLI MUST report and
fail with exit code 6 (`Unsupported Media`), NOT silently skip.

### Unknown Sub-Media

A sub-media identifier not declared by the engine in `gallate.yaml`.
CLI MUST report and fail.

## V

### Verbose

`-v` / `-vv`. Increases diagnostic detail on stderr.

### Quiet

`-q`. Suppresses non-essential output, for scriptable environments.

## W

### Wrapper

The OmegaT integration layer that drives the CLI over GCWP. See
[Protocol glossary § Wrapper](../protocol/00-glossary.md#w). Not a
Shell-layer term, but mentioned for context.