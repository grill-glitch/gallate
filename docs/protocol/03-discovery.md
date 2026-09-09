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

        if features.media.image:
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

Schema: [`schema/manifest.schema.yaml`](../schema/manifest.schema.yaml).

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
| `targets` | optional | Engine-recognition metadata: which games / file shapes this CLI can recognize. See [§ Identify](#identify). |

`id` MUST NOT change between compatible CLI updates. Changing `id`
implies the CLI has become a different compatible implementation (and
the Wrapper may need to re-negotiate).

### `targets` block

The `targets` block tells the Wrapper **which games and file
shapes this CLI can recognize**. The Wrapper uses it as a coarse
pre-filter before invoking `cli identify <path>`.

Three sections:

- `targets.games` — Specific games the CLI can recognize (name +
  engine_versions + optional stable ids). Generic engines (PO file
  tools) MAY leave this empty.
- `targets.formats` — File / directory patterns: `extension` /
  `name_match` / `path_glob` / `directory` / `min_bytes` /
  `kind: file | directory | any`.
- `targets.magic_bytes` — Binary content signatures: `offset` +
  `bytes` (hex by default). Used when extensions lie (renamed
  files, encrypted wrappers).

Schema: [`schema/manifest.schema.yaml`](../schema/manifest.schema.yaml).

Example for an Artemis CLI:

```yaml
type: manifest
protocol: {name: gcwp, version: 1.0}
id: artemis
name: Artemis CLI
version: 1.2.0
engine:
  id: artemis
  versions: ["2.x"]

targets:
  games:
    - name: Higurashi no Naku Koro ni
      engine_versions: ["2.0", "2.1"]
    - name: Umineko no Naku Koro ni
      engine_versions: ["2.1", "2.2"]

  formats:
    - extension: .pfs
      kind: file
    - name_match: system.ini
      kind: file

  magic_bytes:
    - offset: 0
      bytes: "50 46 53 20"     # "PFS " in ASCII
      encoding: hex
      description: PFS archive magic header
```

The `targets` block is **declarative** — the CLI is the source of
truth, and the rule list is whatever the CLI author chose. Different
CLIs MAY use wildly different rule shapes. The Wrapper treats the
`targets` block as a hint, not a contract.

---

## Identify

A CLI MUST also expose a per-path identification operation:

```bash
cli identify <path> --yaml
```

`<path>` is a file or directory. The CLI inspects the path and
returns which of its `targets` rules matched, with confidence and
evidence.

The Wrapper calls `cli identify` after the coarse `manifest.targets`
filter, to confirm a target before extract/inject. The Wrapper MAY
also call `cli identify` on every candidate CLI for the same path
and pick the highest-confidence match — this is how multi-engine
launchers (e.g. one CLI per engine family) triage a new game.

### Response

Schema: [`schema/identify.schema.yaml`](../schema/identify.schema.yaml).

```yaml
type: identify
id: 01HIDENT

target:
  path: /storage/games/higurashi/game.pfs
  kind: file
  size: 421876

matched:
  - engine: artemis
    confidence: high
    rule:
      kind: magic_bytes
      matched: "50 46 53 20"
    game:
      name: Higurashi no Naku Koro ni
      engine_versions: ["2.0", "2.1"]
```

Empty `matched` means the CLI does not handle the target. Multiple
entries are ambiguous candidates; the Wrapper SHOULD sort by
`confidence` descending.

### Confidence

| Level | Meaning |
| --- | --- |
| `high`   | Multiple rules matched (e.g. extension + magic_bytes + known-game id). |
| `medium` | One rule matched. |
| `low`    | Heuristic guess. The Wrapper MUST NOT treat `low` as confirmation without its own sanity check. |

### When to call

The Wrapper calls `cli identify`:

- Before the first extract/inject on a new game (cold start).
- When a user adds a new game directory and asks the wrapper to
  pick a CLI.
- When the wrapper's own `manifest.targets` filter is too coarse
  and a finer answer is needed.

The Wrapper MUST NOT call `cli identify` in a hot loop during
extract/inject — it is a cold-path operation.

---

## Features

The features document describes what the CLI can do.

Interface:

```bash
cli features --yaml
```

Schema: [`schema/features.schema.yaml`](../schema/features.schema.yaml).

Example:

```yaml
type: features

operations:
  extract: true
  inject: true
  build: true
  unpack: true
  repack: true

media:
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
  Operations    Media      Runtime
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
| media | `text` | bool | **Standard** text media (baseline) |
| media | `image` | bool | **Standard** image media (baseline) |
| media | `audio` | bool | Engine-extension media — only present when supported |
| media | `video` | bool | Engine-extension media — only present when supported |
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