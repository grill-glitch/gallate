# 05. Config File

> Status: **Normative**. Defines the structure of `gallate.yaml`,
> the only project-level configuration file.

---

## 5.1 Top-level fields

A standard `gallate.yaml` uses these top-level keys:

```yaml
input:
output:
media:
ignore:
scripts:
engine:
```

| Field    | Type   | Purpose                                  |
| -------- | ------ | ---------------------------------------- |
| `input`  | path   | Game input                               |
| `output` | path   | Default output destination               |
| `media`  | list   | Default media list                       |
| `ignore` | list   | Default ignore patterns                  |
| `scripts`| object | Pre / Post scripts                       |
| `engine` | object | Engine-specific options                  |

All keys are optional. An engine MAY recognize additional keys under
`engine:`; it MUST NOT add new top-level keys that the spec reserves
for standard use.

---

## 5.2 Complete example

```yaml
# gallate.yaml — standard configuration
input: ./game.pfs

media:
  - text
  - image

ignore:
  - "*.tmp"
  - "cache/"
  - "debug.log"

output: ./game-zh.pfs

scripts:
  pre:
    - ./scripts/unpack.py
    - ./scripts/normalize.py
  post:
    - ./scripts/repack.py
    - ./scripts/cleanup.py

engine:
  text_encoding: utf-8
  rebuild_index: true
  # If this engine exposes audio/video as extension media,
  # they would appear here too:
  # audio:
  #   includes: [voice]
  #   excludes: [bgm]
  # video:
  #   includes: [cutscene]
```

---

## 5.3 `input`

```yaml
input: ./game.pfs
```

The original game input. May be:

- A file (e.g. `./game.pfs`)
- A directory (e.g. `./www/`)

The path is resolved relative to the Project Root unless absolute.
Whether a given engine accepts a file or a directory (or both) is
engine-specific.

The CLI does **not** accept input as a CLI argument; the path comes
from `gallate.yaml`.

---

## 5.4 `output`

```yaml
output: ./game-zh.pfs
```

The default output destination. May be overridden on the CLI by
`--output`. See
[09-std-flags.md § Output](./09-std-flags.md#output).

Like `input`, the value may be a file or a directory; the engine
decides which makes sense.

---

## 5.5 `media`

```yaml
media:
  - text
  - image
```

The default media list used when `-e` or `-i` are given without media
flags. See [04-media.md § Default Media](./04-media.md#default-media).

The list is normalized (deduplicated, no order significance) when the
project is loaded. List elements are media identifiers — see
[04-media.md](./04-media.md).

---

## 5.6 `ignore`

```yaml
ignore:
  - "*.tmp"
  - "cache/"
  - "debug.log"
```

Patterns (glob, `.gitignore`-style) that exclude resources from any
operation. See [09-std-flags.md § Ignore](./09-std-flags.md#ignore)
for matching semantics.

---

## 5.7 `scripts`

```yaml
scripts:
  pre: ./scripts/unpack.py
  post: ./scripts/repack.py
```

Or list form for multiple scripts:

```yaml
scripts:
  pre:
    - ./scripts/unpack.py
    - ./scripts/normalize.py
  post:
    - ./scripts/repack.py
    - ./scripts/cleanup.py
```

Execution order:

```text
Input
  ↓
Pre scripts        (definition order, top to bottom)
  ↓
Operation
  ↓
Output
  ↓
Post scripts       (definition order, top to bottom)
```

Default Working Directory for every script: the Project Root. So
`./scripts/pre.py` always means `<ProjectRoot>/scripts/pre.py`.

CLI cannot override `scripts:` — pre/post hooks are configured in
YAML only. This is intentional: pre/post hooks can mutate the input
layout, and silently changing that per-invocation would surprise the
user.

---

## 5.8 `engine`

```yaml
engine:
  text_encoding: utf-8
  rebuild_index: true
```

Engine-specific configuration. Standard CLI MUST NOT interpret any
key inside `engine:` — they are passed through to the engine wrapper
verbatim.

The engine SHOULD use namespaced keys (e.g. `text_encoding`) to avoid
collisions. The CLI accepts any key.

Engine-extension media / sub-media are also configured under
`engine:`, see
[04-media.md § Sub-Media](./04-media.md#sub-media) and
[08-engine-extensions.md](./08-engine-extensions.md).

---

## 5.9 Reserved top-level keys

The following keys are reserved for future spec use and MUST NOT be
used by engines today:

```text
hooks       # reserved
watch       # reserved
profile     # reserved
```

Reserved namespaces:

```text
gallate.*   # reserved for project-level config (not engine options)
gcwp.*      # reserved for protocol-level options
```

---

## 5.10 Path resolution

All relative paths inside `gallate.yaml` are resolved against the
**Project Root** (the directory containing `gallate.yaml`):

```yaml
# gallate.yaml at /home/me/projects/gamelate.yaml
input: ./game.pfs
```

`./game.pfs` resolves to `/home/me/projects/game.pfs`, not
`/home/me/game.pfs` (the shell's CWD).

Absolute paths are used as-is. This rule applies to:

```text
input
output
ignore
scripts.pre / scripts.post
engine.* paths
```