# 09. Diagnostics

> Status: **Normative**. Defines the two non-protocol channels
> (stderr) and the structured error model used in the protocol channels.

---

## Channels

```text
stdout  → machine protocol     (Response / Events)
stderr  → human diagnostics    (logs / warnings / progress to user)
exit    → final result         (integer code)
```

The boundary is strict:

- `stdout` is for protocol only. CLI MUST NOT print free-form text or
  decorative progress bars to stdout.
- `stderr` is for humans. CLI MAY use ANSI colors, progress bars,
  verbose dumps. Wrapper MUST NOT parse stderr.

Wrapper MUST NOT determine operation state by parsing stderr. See
[02-core-protocol.md § Channels](./02-core-protocol.md#channels).

---

## stderr content examples

```text
Scanning archive...
Extracting text from scene_037.bin...
warning: foo.dat uses unsupported format, skipping

✓ 317 files processed
✓ 8421 strings extracted
```

These lines are for the operator's terminal and the wrapper's log file.
Their format is engine-specific and may change without notice.

---

## Structured errors

Errors that the Wrapper must classify MUST go through the protocol
(`event: error`) with a stable `code`:

```yaml
type: event
event: error
code: INVALID_INPUT
message: Input archive is corrupted
path: ./game.pfs
```

### Required fields

| Field | Notes |
| --- | --- |
| `code` | Stable, machine-classified. UPPER_SNAKE_CASE recommended. |
| `message` | Human-readable. MAY change between versions. |

### Optional fields

| Field | Notes |
| --- | --- |
| `path` | Resource path the error refers to. |
| `file` | Source file (when different from `path`). |
| `line` | Line number. |
| `offset` | Character offset. |
| `length` | Region length. |
| `resource` | Logical resource id (engine-defined). |
| `details` | Free-form additional context (object). |

### Wrapper rule

```text
WRONG:
    if "corrupted" in message:
        show_repair_dialog

CORRECT:
    if code == "INVALID_INPUT":
        show_repair_dialog
```

Wrapper MUST key off `code`, never `message`.

---

## Stable error codes

CLI MUST pick stable codes for classifiable errors:

```text
INVALID_INPUT
INVALID_CONFIG
UNSUPPORTED_OPERATION
UNSUPPORTED_FORMAT
UNSUPPORTED_ENCODING
FILE_NOT_FOUND
PERMISSION_DENIED
ARCHIVE_CORRUPTED
CHECKSUM_MISMATCH
OUT_OF_MEMORY
TIMEOUT
INTERNAL_ERROR
PROTOCOL_ERROR
```

New codes MAY be added in minor versions; codes MUST NOT be repurposed.

See [12-compatibility.md § Stable Identifiers](./12-compatibility.md).

---

## Warning vs Error

A `warning` event MUST NOT cause a non-zero exit code unless the CLI
explicitly promotes it. `error` events SHOULD result in a non-zero exit
code (typically `1` or a more specific code) but a CLI MAY continue
running for resilient batch jobs.

Recommended mapping:

```text
warning event      → no exit code change
error event        → exit code 1
protocol violation → exit code 7
internal crash     → exit code 8
```

CLI MAY choose its own mapping, but the standard codes are reserved per
[02-core-protocol.md § Exit Codes](./02-core-protocol.md#exit-codes).

---

## Debug / Verbose

CLI MAY support `--verbose` or `--debug` flags. These affect stderr
volume, never the protocol stream:

```text
--verbose    → more stderr lines
--debug      → verbose + engine internals (still stderr)
```

CLI MUST NOT alter the protocol stream when verbose is enabled.

---

## Cancellation diagnostics

When cancelled, CLI MAY emit a final stderr line for the operator:

```text
warning: operation cancelled, cleaning up temp files
```

But the protocol MUST show `cancelled` event and exit code `6`.