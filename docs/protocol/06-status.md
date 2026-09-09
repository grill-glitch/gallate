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
cli status --yaml
```

If the CLI is currently running an operation, this returns a snapshot
of that operation. If idle, the state is `idle`.

---

## Status document

Schema: [`schema/status.schema.json`](../schema/status.schema.json).

Example:

```yaml
type: status
state: running

operation: extract

phase: extracting

progress:
  current: 72
  total: 100

current:
  path: script/scene_072.bin

started_at: 2026-09-09T12:34:56Z
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