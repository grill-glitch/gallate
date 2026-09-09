# 05. Events

> Status: **Normative**. Defines the live event stream a CLI emits to
> stdout during an operation.

Events are the Wrapper's primary real-time signal. They MUST be in YAML
Line Protocol format. See
[02-core-protocol.md § YAML Line Protocol](./02-core-protocol.md#yaml-line-protocol).

---

## Standard events

| Event | Required by | Meaning |
| --- | --- | --- |
| `started` | Basic | The operation has begun. |
| `phase` | Standard | A transition between sub-phases. |
| `progress` | Standard | A progress update. |
| `file` | Standard | A per-file action. |
| `resource` | Standard | A per-resource action (engine-level granularity). |
| `warning` | Standard | A non-fatal warning. |
| `error` | Standard | A recoverable error. |
| `validation` | Standard | A validation finding. |
| `statistics` | Standard | A statistics snapshot (typically at completion). |
| `completed` | Basic | The operation ended successfully. |
| `cancelled` | Full | The operation was cancelled. |

Schema: [`schema/event.schema.json`](../schema/event.schema.json).

---

## started

```yaml
type: event
event: started
id: 01HXYZ
operation: extract
```

---

## phase

```yaml
type: event
event: phase
name: scanning
```

Suggested phase names:

```text
preparing
scanning
extracting
processing
writing
finalizing
```

Phase names are engine-specific; the standard names above are
recommended but not mandatory.

---

## progress

```yaml
type: event
event: progress
current: 37
total: 100
```

Indeterminate progress is allowed:

```yaml
type: event
event: progress
current: 37
total: null
```

Wrapper MUST support indeterminate progress.

---

## file

```yaml
type: event
event: file
action: extract
path: script/scene_037.bin
```

Standard actions:

```text
scan
read
write
create
modify
skip
extract
inject
delete
```

---

## resource

Same shape as `file`, but engine-resource granular:

```yaml
type: event
event: resource
action: extract
path: scenes/day1/scene_037/string_0042
```

---

## warning

```yaml
type: event
event: warning
code: UNSUPPORTED_FORMAT
message: Unsupported resource format
path: foo.dat
```

`warning` MUST NOT cause a non-zero exit code unless the CLI
explicitly promotes it. See [09-diagnostics.md](./09-diagnostics.md).

---

## error

```yaml
type: event
event: error
code: INVALID_INPUT
message: Input archive is corrupted
path: ./game.pfs
```

`error.code` is the **stable** identifier Wrapper MUST use to classify
errors. `message` MAY change between versions. See
[12-compatibility.md § Stable Identifiers](./12-compatibility.md).

---

## validation

```yaml
type: event
event: validation
rule: placeholder
severity: error

source: Hello {player}
target: 你好

message: Required placeholder is missing: {player}

file: script/scene_037.bin
line: 42
offset: 12
length: 8
```

See [08-validation.md](./08-validation.md).

---

## statistics

```yaml
type: event
event: statistics

statistics:
  files:
    processed: 317
  text:
    extracted: 8421
```

The `statistics` event usually carries the final snapshot. See
[07-statistics.md](./07-statistics.md).

---

## completed

```yaml
type: event
event: completed

statistics:
  files:
    processed: 317
```

`completed` means the operation ended successfully. CLI MUST emit this
event before exit 0. The CLI process MUST then exit.

---

## cancelled

```yaml
type: event
event: cancelled
```

CLI MUST emit `cancelled` after receiving a `cancel` command (see
[11-process.md § Cancellation](./11-process.md#cancellation)) and
before exit code 6.

---

## Event ordering

```text
1. started                    MUST
2. zero or more of:           optional
   phase, progress, file, resource,
   warning, error, validation,
   statistics
3. exactly one of:            MUST
   completed, cancelled
```

A second terminal event is a protocol error.