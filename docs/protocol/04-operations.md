# 04. Operations

> Status: **Normative**. Defines the unit of work a Wrapper asks a CLI to
> perform: shape, arguments, inputs, outputs, and options.

---

## Standard operations

```text
extract       read engine resources, write translation assets
inject        read translated assets, write engine resources
build         produce final packaged output
unpack        open an engine archive
repack        close an engine archive
```

CLI MAY support additional operations. Standard operation names MUST
NOT be redefined; new operations MUST use names not in the standard
list.

---

## Operation Request

Schema: [`schema/request.schema.json`](../schema/request.schema.json).

Wrapper sends a single `request` message over stdin:

```yaml
type: request
id: 01HXYZABCDEF
operation: extract

input:
  - ./game.pfs

output:
  - ./translation

options: {}
```

### Fields

| Field | Required | Notes |
| --- | --- | --- |
| `type` | ✓ | MUST be `request`. |
| `id` | ✓ | Operation ID. Used to correlate every event / status / final exit. |
| `operation` | ✓ | One of the standard names, or an engine-extension name. |
| `input` | optional | List of paths or structured path objects. |
| `output` | optional | List of paths or structured path objects. |
| `options` | optional | Operation-level structured configuration. |
| `ignore` | optional | List of ignore patterns. |

The `id` field is opaque to the CLI but is the single correlation key
across the event stream. Wrapper SHOULD use a ULID or UUIDv7.

---

## Input / Output

A path can be a plain string or a structured object:

```yaml
# Plain (CLI infers file vs directory)
- ./game.pfs

# Structured (explicit kind)
- path: ./game.pfs
  kind: file

- path: ./data
  kind: directory
```

CLI MUST be able to handle both files and directories. Wrapper SHOULD
use the structured form whenever ambiguity matters.

### Path resolution rule

```text
relative path   → resolved relative to the gallate.yaml Project Root
absolute path   → used as-is
```

See [10-configuration.md § Path Resolution](./10-configuration.md).

---

## Ignore

Ignore rules belong to the **operation configuration**, not to the
CLI itself.

```yaml
ignore:
  - "**/*.tmp"
  - "**/cache/**"
  - system.dat
```

Glob implementation notes belong in the CLI documentation. GCWP does
not pin a glob flavor.

Wrapper MUST NOT silently modify the ignore list. See
[`Documents/通用行为规范.txt § Ignore`](https://github.com/grill-glitch/Documents)
for the matching semantics (`*`, `**`, `?`, `directory/`).

---

## Options

Engine-specific options live under `options` with engine namespacing:

```yaml
options:
  artemis.text_encoding: shift-jis
  artemis.rebuild_index: true
```

Reserved namespaces:

- `gallate.*` — reserved for future use by the Wrapper itself.
- `gcwp.*` — reserved for future protocol-level options.

---

## Engine-extension operations

CLI MAY define engine-specific operations:

```text
analyze
list
verify
patch
```

A Wrapper that encounters an unknown operation type MUST reject the
request before launching the CLI. CLI that receives an unknown
operation MUST reject it with exit code `4` (`unsupported operation`).

---

## Operation lifetime

A single request yields exactly one of:

```text
completed      success
failed         exit code != 0
cancelled      via stdin command
```

See [11-process.md](./11-process.md) for the full process lifecycle.