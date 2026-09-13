# 06. Status

> Status: **Normative**. Defines the on-demand state snapshot a CLI
> can return in response to a status query.

Status is a **point-in-time** query. It complements, not replaces,
the event stream (see [05-events.md](./05-events.md)).

---

## Status vs Event vs Statistics

```text
Event       → during the operation, real-time
Status      → on demand, snapshot of "now"
Statistics  → cumulative, what has been done
```

These three MUST be strictly separated.

---

## Status query

CLI MUST support a status interface if `features.runtime.status` is true.

Interface:

```bash
cli status
```

If the CLI is currently running an operation, this returns a snapshot
of that operation. If idle, the state is `idle`.

---

## Status document

Schema: [`schema/status.schema.yaml`](../schema/status.schema.yaml).

Example:

```json
{
  "type": "status",
  "state": "running",

  "operation": "extract",
  "phase": "extracting",

  "progress": {
    "current": 72,
    "total": 100
  },

  "current": {
    "path": "script/scene_072.bin"
  },

  "started_at": "2026-09-09T12:34:56Z"
}
```

### Fields

| Field | Required | Notes |
| --- | --- | --- |
| `state` | ✓ | Lifecycle state (see below). |
| `operation` | optional | Currently running operation name. |
| `phase` | optional | Current sub-phase within `running`. |
| `progress` | optional | `current` / `total` pair; `total` may be `null`. |
| `current` | optional | Currently processed resource / file. |
| `started_at` | optional | ISO-8601 timestamp. |

---

## Status on the wire

Status is **not** an event in the operation stream. It is a
**synchronous query/response**:

```text
Wrapper                          CLI
   │                              │
   │  ── status.jsonl ───▶  │   (a single line, one JSON object)
   │                              │   OR alternatively a `cli status`
   │  ◀── single status doc ───  │   invocation on a dedicated pipe
   │                              │
```

There are **two** equivalent transports. Pick one per Wrapper; do not
mix them in the same CLI session:

### A. Inline status stream

```jsonl
# Wrapper → CLI over stdin (any point during running)
{"type":"status-query","id":"01HSTATUS"}

# CLI → Wrapper over stdout (single line, then back to events)
{"type":"status","state":"running","operation":"extract","phase":"extracting","progress":{"current":72,"total":100}}
```

The CLI returns **exactly one** status document in response, then
resumes the normal event stream.

### B. Dedicated invocation

```bash
# Wrapper spawns a separate CLI process (or reuses the existing one
# with a side-band fd) and asks:
$ cli status
```

This avoids polluting the operation's stdin/stdout with status
queries. Wrappers MAY prefer this when long-running operations have
many status polls.

### Wire-format

The status document follows the same wire format as every other
GCWP message: one JSON object per line on stdout (the standard
[JSON Line Protocol](./02-core-protocol.md#json-line-protocol)
format). There is no separate YAML form for status. If you see
`cli status` returning anything other than JSON Lines, that is a
protocol violation by the CLI.

---

## Status query message

Schema: [`schema/status-query.schema.yaml`](../schema/status-query.schema.yaml).

```jsonl
{"type":"status-query","id":"01HSTATUS"}
```

The Wrapper MUST include a query id, and the CLI MUST echo the same id
back in its `type: status` response so the Wrapper can correlate.

---

## State

Standard states:

```text
idle
preparing
running
completed
failed
cancelled
```

Rules:

- `running` is the only state with a `phase`.
- `completed` / `failed` / `cancelled` are terminal; the CLI exits
  shortly after entering them.
- `preparing` is the time between receiving the request and emitting
  the first progress event.

---

## Phase is not State

DO NOT model sub-phases as separate states.

```text
WRONG:
  state = extracting

CORRECT:
  state = running
  phase = extracting
```

Phases live under the `running` state. See [05-events.md § phase](./05-events.md#phase).

---

## Status vs Phase transition events

Both report phase, but:

```text
Event  phase         emitted by CLI automatically at transitions
Status phase        read by Wrapper when it asks "where are you?"
```

A Wrapper MAY subscribe to the `phase` event stream instead of polling
status, if real-time phase transitions are sufficient.