# 03. Discovery

> Status: **Normative**. CLI MUST expose `manifest` and `features` for
> Wrapper capability discovery.

---

## Why capability discovery

```text
WRONG (anti-pattern):

        if cli == "artemis":
            show_image
        elif cli == "renpy":
            show_image
        elif …

CORRECT (per-feature):

        if features.resources.image:
            show_image
```

Wrapper MUST drive all UI and routing decisions from the `features`
document the CLI returns. CLI id, name, and engine id are stable
identifiers — but the Wrapper MUST NOT infer behavior.

---

## Manifest

The manifest is the CLI's identity document.

Interface:

```bash
cli manifest --yaml
```

Schema: [`schema/manifest.schema.json`](../schema/manifest.schema.json).

Example:

```yaml
type: manifest
protocol:
  name: gcwp
  version: 1.0
id: artemis
name: Artemis CLI
version: 1.2.0
engine:
  id: artemis
  versions:
    - 2.x
```

### Fields

| Field | Required | Notes |
| --- | --- | --- |
| `id` | ✓ | Stable CLI identifier. See [Stable Identifiers](./12-compatibility.md#stable-identifiers). |
| `name` | ✓ | Human-readable name. May change between releases. |
| `version` | ✓ | CLI version. |
| `protocol` | ✓ | Object with `name` and `version`. |
| `engine` | optional | Engine identification; required for engine-specific CLIs. |

`id` MUST NOT change between compatible CLI updates. Changing `id`
implies the CLI has become a different compatible implementation (and
the Wrapper may need to re-negotiate).

---

## Features

The features document describes what the CLI can do.

Interface:

```bash
cli features --yaml
```

Schema: [`schema/features.schema.json`](../schema/features.schema.json).

Example:

```yaml
type: features

operations:
  extract: true
  inject: true
  build: true
  unpack: true
  repack: true

resources:
  text: true
  image: true
  audio: false
  video: false

validation:
  syntax: true
  regex: true
  placeholder: true
  constraint: true

runtime:
  events: true
  status: true
  statistics: true
  cancellation: true
```

### Four independent dimensions

```text
                CLI
                 │
       ┌─────────┼──────────┐
       │         │          │
  Operations  Resources  Runtime
       │         │          │
  extract     text      status
  inject      image     events
  build       audio     statistics
  unpack      video     cancellation
  repack
                 │
            Validation
                 │
          ┌──────┼──────┐
          │      │      │
        regex  placeholder  constraint
```

These four dimensions are independent. A CLI MAY support any subset of
each dimension.

### Fields

| Group | Field | Type | Meaning |
| --- | --- | --- | --- |
| operations | `extract` | bool | Resource extraction |
| operations | `inject` | bool | Translation injection |
| operations | `build` | bool | Engine build |
| operations | `unpack` | bool | Engine archive unpack |
| operations | `repack` | bool | Engine archive repack |
| resources | `text` | bool | **Standard** text media (baseline) |
| resources | `image` | bool | **Standard** image media (baseline) |
| resources | `audio` | bool | Engine-extension media — only present when supported |
| resources | `video` | bool | Engine-extension media — only present when supported |
| validation | `syntax` | bool | Generic syntax check (engine-defined) |
| validation | `regex` | bool | Regex rules |
| validation | `placeholder` | bool | Placeholder preservation |
| validation | `constraint` | bool | Constraint rules |
| runtime | `events` | bool | Event streaming |
| runtime | `status` | bool | Status query |
| runtime | `statistics` | bool | Statistics emission |
| runtime | `cancellation` | bool | Cancellation support |

> **Media baseline vs extension**: A Wrapper MAY assume `text` and
> `image` are baseline (every gallate CLI declares them, with at least
> `text: true`). `audio`, `video`, and any other keys (e.g. `font`)
> are engine-extension and MUST NOT be assumed present. The full
> Shell-layer definition of standard vs extension media is in
> [docs/shell-layer/04-media.md](../../shell-layer/04-media.md).

### Negative truth

Unsupported capabilities MUST be reported as `false`, not omitted:

```yaml
runtime:
  status: false
  statistics: false

validation:
  syntax: false
```

Wrapper MUST NOT assume a capability exists just because it is missing
from the `features` document.

---

## Discovery order

```text
1. Start CLI
2. Announce / check protocol version
3. Get manifest
4. Get features
5. Get validation rules
6. Build operation request
8. Consume events
9. Get statistics
10. Check exit code
```

See [11-process.md](./11-process.md) for the full lifecycle.

---

## Conformance tier mapping

The capabilities a CLI exposes determine its conformance tier:

```text
Basic    = manifest + features + one operation + exit codes
Standard = Basic + events + statistics + validation
Full     = Standard + cancellation + status streaming + diagnostics
```

See [13-conformance.md](./13-conformance.md).