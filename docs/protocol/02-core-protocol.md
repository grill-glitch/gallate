# 02. Core Protocol

> Status: **Normative**. Defines the lowest layer of GCWP: the version
> string, the wire format, the channels, and the exit codes.

This chapter is intentionally independent of any specific operation
(`extract`, `inject`, …). For operations, see [04-operations.md](./04-operations.md).

---

## Communication model

CLI is an independent process.

Wrapper starts CLI, then communicates with it via standard I/O:

```text
stdin   ← Request / Command (from Wrapper)
stdout  → Response / Event stream (to Wrapper)
stderr  → Human-readable diagnostics (to user / log)
exit    → Final result (to Wrapper)
```

The machine-readable channels (stdin and stdout) use the **YAML Line
Protocol**: one YAML document per line. Plain text or free-form log
output MUST NOT appear on stdout — it MUST go to stderr.

---

## YAML Line Protocol

Every line on stdin/stdout that carries protocol content MUST be a
single YAML document. Flow-mapping single-line form is recommended for
compactness:

```yaml
{type: event, event: started, operation: extract}
{type: event, event: progress, current: 10, total: 100}
{type: event, event: progress, current: 50, total: 100}
{type: event, event: completed}
```

Receivers MUST treat each line as an independent document.

Multi-line block YAML is allowed when a single line would be unwieldy,
but the receiver MUST still treat each line as a separate YAML document
and MUST NOT require cross-line parsing.

JSON Lines (NDJSON / JSONL) is **not** part of GCWP. Implementations MAY
support both for legacy reasons but new fields MUST be specified in
YAML.

---

## Channels

| Channel | Direction | Content |
| --- | --- | --- |
| stdin | Wrapper → CLI | One or more protocol messages: usually one operation request, optionally a `cancel` command. |
| stdout | CLI → Wrapper | The initial `response`, then the event stream. |
| stderr | CLI → user | Human-readable diagnostics. NOT protocol. |
| exit | CLI → OS | Integer exit code. |

---

## Protocol version

Every GCWP message MUST declare the protocol version. The version string
is `MAJOR.MINOR` (e.g. `1.0`, `1.1`, `2.0`).

```yaml
type: protocol
name: gcwp
version: 1.0
```

### MAJOR

Increments on incompatible changes.

```text
1.x → 2.x   wrapper may refuse unsupported MAJOR
```

### MINOR

Increments on backwards-compatible additions.

```text
1.0 → 1.1   old Wrappers ignore unknown fields
```

See [12-compatibility.md](./12-compatibility.md) for full rules.

---

## Message types

| `type` | Direction | Purpose |
| --- | --- | --- |
| `protocol` | either | Announce / check protocol version |
| `request` | Wrapper → CLI | Operation request |
| `command` | Wrapper → CLI | Out-of-band instruction (currently: `cancel`) |
| `response` | CLI → Wrapper | Acknowledge a request and announce operation id |
| `event` | CLI → Wrapper | One entry in the event stream |
| `status` | CLI → Wrapper | Reply to a status query (see [06-status.md](./06-status.md)) |
| `status-query` | Wrapper → CLI | Ask for a status snapshot mid-operation |
| `validation-result` | CLI → Wrapper | A validation finding during/after an operation |

> **Note**: `validation-rules` is **not** a wire message — it is the
> `type` field of the document returned by `cli validation --yaml`
> during discovery. See
> [validation-rules.schema.yaml](../schema/validation-rules.schema.yaml).
> The wire-shape payload of validation findings is `event: validation`
> with `severity` and `rule` fields; see
> [validation-result.schema.yaml](../schema/validation-result.schema.yaml).

All message types are defined as YAML Schema (JSON Schema draft-07
semantics) under [`schema/`](../schema/).

---

## Operation flow (skeleton)

```text
Wrapper                          CLI
   │                              │
   │  ── request ──────────────▶  │   (one operation)
   │                              │
   │  ◀── response ────────────  │   (acknowledgement)
   │                              │
   │  ◀── event started ───────  │
   │  ◀── event progress ──────  │
   │  ◀── event file ──────────  │
   │  ◀── event warning ───────  │
   │  ◀── event completed ─────  │
   │                              │
   │  exit code                  │
```

If the Wrapper wants to abort mid-flight:

```text
Wrapper                          CLI
   │                              │
   │  ── command cancel ───────▶  │
   │                              │
   │  ◀── event cancelled ─────  │
   │  exit code 6                 │
```

---

## Exit codes

Standard exit codes — semantics MUST NOT change:

| Code | Meaning |
| --- | --- |
| `0` | success |
| `1` | operation failed |
| `2` | invalid arguments |
| `3` | invalid configuration |
| `4` | unsupported operation |
| `5` | validation failed |
| `6` | cancelled |
| `7` | protocol error |
| `8` | internal error |

CLI MAY define additional exit codes; the standard codes MUST keep
their meaning.

---

## Relationship between Exit Code and Event

```text
Event     → process information (during the operation)
Exit code → final result (after the operation)
```

Wrapper MUST consider both. It MUST NOT determine the final outcome from
the last event alone.

Example:

```text
started
progress
error               (event: stream-level failure)
completed           (event: stream closed cleanly)
exit 1              (process-level failure)
```

```text
started
progress
cancelled
exit 6
```