# 00. Glossary

> Status: **Normative**. CLI and Wrapper MUST use these terms in the
> same sense throughout their implementation and documentation.

---

## A

### Architecture

The three-layer arrangement:

```text
OmegaT → Wrapper → CLI → Game Engine
```

### Argument

A single key/value or single flag passed to an operation. Distinct from
**Options** (operation-level structured configuration) and from
**Input / Output** (filesystem targets).

---

## C

### Cancellation

The Wrapper-initiated stopping of an in-flight operation, via the
`cancel` command over stdin. See [11-process.md](./11-process.md).

### CLI (CLI Tool)

An independent executable that targets **one** specific game engine,
engine family, or resource format. Speaks GCWP. Examples:
`artemis-cli`, `renpy-cli`.

### Command

A short message from Wrapper to CLI over stdin that is **not** an
operation request. Currently the only standard command is `cancel`.

### Conformance Tier

The level of GCWP coverage a CLI claims: Basic / Standard / Full.
See [13-conformance.md](./13-conformance.md).

### Core Protocol

The wire-format layer: protocol version, line protocol, stdin/stdout
channels, exit codes. See [02-core-protocol.md](./02-core-protocol.md).

---

## D

### Diagnostics

Human-readable information emitted by CLI on **stderr**. NOT part of
the machine protocol. See [09-diagnostics.md](./09-diagnostics.md).

### Discovery

The process of learning what a CLI is (`manifest`) and what it can do
(`features`). See [03-discovery.md](./03-discovery.md).

---

## E

### Engine

The target game engine, file format, or runtime that a CLI wraps. Distinct
from the engine's domain (e.g. `renpy-cli` targets the **Ren'Py** engine).

### Event

A structured message emitted by CLI on stdout during an operation.
See [05-events.md](./05-events.md).

### Exit Code

The integer returned by the CLI process at termination. Standard values
defined in [02-core-protocol.md § Exit Codes](./02-core-protocol.md#exit-codes).

---

## F

### Features

The static capability description a CLI returns from `cli features`.
See [03-discovery.md](./03-discovery.md).

### Full Conformance

Top conformance tier. Includes cancellation, status streaming, full
diagnostics, and so on. See [13-conformance.md](./13-conformance.md).

---

## G

### GCWP

**Gamelate CLI–Wrapper Protocol.** The protocol defined by this specification.
Despite the rename of the umbrella project to `gallate`, the protocol
short-name **GCWP** is retained for historical anchor and recognizability.

### gallate.yaml

The **project-level** YAML configuration file. Described in the companion
specification
[`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents).
GCWP only consumes its parsed result, never the raw file.

---

## H

### Help Output

The free-form, human-readable text a CLI prints when invoked
without arguments or with `--help`. Help output is **not** part
of the wire protocol; the Wrapper MUST NOT parse it.

---

## I

### Identify

The `cli identify <path>` operation. Returns a list of matched
recognition rules from `manifest.targets`, each tagged with a
confidence level (`high` / `medium` / `low`). The Wrapper uses
this to pick the right CLI for a candidate game path. See
[03-discovery.md § Identify](./03-discovery.md#identify).

### ID (Operation ID)

The ULID/UUID the Wrapper assigns to each operation request, used to
correlate events, status snapshots, and the final exit.

### Ignore

A glob / path pattern list that filters resources out of an operation.
Defined in [04-operations.md](./04-operations.md#ignore) and in
[`gallate.yaml` § Ignore](https://github.com/grill-glitch/Documents).

### Indeterminate Progress

A progress report with `total: null`. See
[05-events.md](./05-events.md#progress).

---

## J

### JSON Unit File

The standard unit-file format produced/consumed by OmegaT — one JSON
document per logical translation domain, holding a flat `units`
array. GCWP does not touch unit files directly; Wrapper maps GCWP
operations to and from the JSON unit documents described at the
Shell layer
([12-file-structure.md](../shell-layer/12-file-structure.md)).

---

## K

### (reserved)

No K-terms yet.

---

## L

### JSON Line Protocol

The wire format for messages on stdout and stdin: one JSON object
per line — the standard [JSON Lines][jsonl] (NDJSON) format.
YAML is **not** part of the wire. See
[02-core-protocol.md § JSON Line Protocol](./02-core-protocol.md#json-line-protocol).

[jsonl]: https://jsonlines.org/

---

## M

### Manifest

The CLI identity document. Returned by `cli manifest`. See
[03-discovery.md § Manifest](./03-discovery.md#manifest).

---

## N

### (reserved)

No N-terms yet.

---

## O

### Operation

A unit of work requested by Wrapper and executed by CLI. Standard
operations: `extract`, `inject`, `build`, `unpack`, `repack`.
See [04-operations.md](./04-operations.md).

### Operation Request

The structured message Wrapper sends to CLI over stdin at the start of
an operation. See [04-operations.md § Operation Request](./04-operations.md#operation-request).

### Options

Operation-level structured configuration (e.g. `text_encoding`,
`rebuild_index`). Engine-namespaced keys.

---

## P

### Phase

A label inside the `running` state. Distinct from **State** (which is
the overall lifecycle phase). See
[06-status.md](./06-status.md#state).

### Placeholder Rule

A validation rule that requires a specific placeholder pattern (e.g.
`{player}`) to be preserved in the target. See
[08-validation.md § Placeholder](./08-validation.md#placeholder-rule).

### Protocol Version

A `MAJOR.MINOR` string. Major bump signals breakage; minor bump signals
backwards-compatible additions. See
[12-compatibility.md](./12-compatibility.md).

---

## Q

### (reserved)

No Q-terms yet.

---

## R

### Regex Rule

A validation rule backed by a regular expression. See
[08-validation.md § Regex](./08-validation.md#regex-rule).

### Request

Synonym for **Operation Request**.

### Response

The CLI's reply at the start of an operation (acknowledging the request
and announcing the chosen operation ID). Subsequent output on stdout is
the **event stream**. See [02-core-protocol.md](./02-core-protocol.md).

---

## S

### Schema

A JSON Schema document under `schema/` that defines the exact wire
shape of a message type.

### Scope (Validation)

What a validation rule applies to: `text`, `source`, `target`,
`placeholder`, `metadata`, `resource`. See
[08-validation.md § Scope](./08-validation.md#scope).

### Severity

How strictly a validation rule should be enforced: `info`, `warning`,
`error`. See [08-validation.md § Severity](./08-validation.md#severity).

### Stable Identifier

An identifier whose value MUST NOT change between compatible versions:
CLI id, Engine id, Operation id, Feature names, Validation rule id,
Error code. See [12-compatibility.md](./12-compatibility.md).

### State

The overall lifecycle phase of an operation: `idle`, `preparing`,
`running`, `completed`, `failed`, `cancelled`. See
[06-status.md](./06-status.md).

### Statistics

The result metrics emitted at the end of an operation. Distinct from
**Status** (now) and **Event** (during). See
[07-statistics.md](./07-statistics.md).

### Status

A snapshot of the CLI's current state, queried on demand. See
[06-status.md](./06-status.md).

---

## T

### (reserved)

No T-terms yet.

---

## U

### Unknown Field

A field in a protocol message that the receiver does not recognize.
Receivers MUST ignore unknown fields per [12-compatibility.md](./12-compatibility.md).
Exception: unknown MAJOR protocol version, event type, operation type,
or validation type may be rejected.

### Unknown Operation

An operation type the CLI does not implement. CLI MUST reject with
exit code 4 (`unsupported operation`).

### Unknown Event

An event type the Wrapper does not recognize. Wrapper MUST ignore.

---

## V

### Validation Rule

A named rule the CLI exposes for OmegaT to apply on translated text.
See [08-validation.md](./08-validation.md).

---

## W

### Wrapper

The only OmegaT integration point. Owns GCWP client, project config
loading, event/status aggregation, OmegaT glue. Must NOT contain
engine-specific logic. See [01-architecture.md](./01-architecture.md).

---

## Y

### YAML vs JSON

GCWP picks one format per role:

| Role | Format | Why |
| --- | --- | --- |
| Project config (`gallate.yaml`) | YAML | Edited by humans; comments and multi-line strings matter. |
| Wire protocol (stdin / stdout) | JSON Line Protocol for streaming, JSON for one-shot discovery | Machine-to-machine; never read by a human. |
| Reference snapshots of discovery output (e.g. `examples/full-cli/manifest.json`) | JSON | One document; the schema is the source of truth. |
| Project state (`.meta.json`) | JSON | Machine-derived; the schema is the source of truth. |
| Translation state (`text/units/*.json`, format `gallate.translation`) | JSON | Human-edited values live inside a JSON container so the data shape stays machine-validatable. |

YAML appears **only** as `gallate.yaml` (the project config file
editable by humans). There is no `--yaml` flag; CLI discovery
commands (`cli manifest`, `cli features`, `cli validation`,
`cli identify <path>`, `cli status`) emit JSON on stdout.

---

## Z

### (reserved)

No Z-terms yet.