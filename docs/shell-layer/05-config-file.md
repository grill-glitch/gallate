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
text:
image:
audio:
video:
engine:
```

| Field    | Type   | Purpose                                  |
| -------- | ------ | ---------------------------------------- |
| `input`  | path   | Game input                               |
| `output` | path   | Default output destination               |
| `media`  | list   | Default media list                       |
| `ignore` | list   | Default ignore patterns                  |
| `scripts`| object | Pre / Post scripts                       |
| `text`   | object | Text-media output configuration          |
| `image`  | object | Image-media output configuration         |
| `audio`  | object | Audio-media output configuration         |
| `video`  | object | Video-media output configuration         |
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

text:
  format: xliff
  layout: flat
  metadata:
    original_file: true
    source_context: true
    location: true
    engine_path: true
  hardcoded:
    context_lines: 3
    max_bytes: 4096
    engine_extensions:
      - .py
      - .lua
      - .rpy
      - .ks

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

## 5.8 Per-media output configuration

Each standard media has its own top-level config block that
controls how files in `text/`, `image/`, `audio/`, `video/` are
structured and what metadata they carry. Engines MAY add their own
per-extension-media blocks under the same pattern.

### `text`

```yaml
text:
  format: xliff            # xliff | po | json | engine-extension
  layout: flat             # flat | mirror | single (see 12-file-structure.md)
  sub_media_dirs: false    # ignored (sub-media live inside files for text)

  # Metadata fields every translation unit MUST carry.
  metadata:
    original_file: true        # source path inside the game archive
    source_context: true       # surrounding code/snippet (for hardcoded)
    location: true             # line / offset / length when known
    engine_path: true          # engine-internal logical path

  # Source-context capture for hardcoded strings.
  hardcoded:
    context_lines: 3           # lines of surrounding source to capture
    max_bytes: 4096            # cap on context payload per unit
    engine_extensions:         # which engine file types count as code
      - .py
      - .lua
      - .js
      - .rpy
      - .ks
```

#### Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `format` | enum | Output format. Standard: `xliff` / `po` / `json`. |
| `layout` | enum | File layout. Standard: `flat` / `mirror` / `single`. See [12-file-structure.md](./12-file-structure.md). |
| `metadata.original_file` | bool | If true, every `<trans-unit>` carries an `original-file` attribute naming the source resource path inside the game archive. Default: `true`. |
| `metadata.source_context` | bool | If true, every `text.hardcoded` unit carries a `source-context` field with the surrounding source code (see below). Default: `true`. |
| `metadata.location` | bool | If true, units carry `line` / `offset` / `length` when the engine knows them. Default: `true`. |
| `metadata.engine_path` | bool | If true, units carry the engine-internal logical path (engine-defined). Default: `true`. |
| `hardcoded.context_lines` | int | Lines of surrounding code to capture for `text.hardcoded` units. Default: `3`. |
| `hardcoded.max_bytes` | int | Upper bound on the captured context payload, per unit. Default: `4096`. |
| `hardcoded.engine_extensions` | list | File extensions the engine treats as code for context capture. Empty list = engine decides. |

#### `original-file`

The `original-file` field lets a translator know exactly which file
inside the game archive a translation unit came from. Without it,
"errors" or follow-up QA cannot trace a missing translation back to
its origin.

Example XLIFF unit:

```xml
<trans-unit id="tu-0042" original-file="scenes/day1/scene_001.bin">
  <source>Hello {player}</source>
  <target>你好 {player}</target>
</trans-unit>
```

The CLI MUST emit `original-file` whenever the value is knowable.
When `metadata.original_file` is `false`, the CLI MAY omit it but
Wrapper / OmegaT SHOULD treat its absence as "unknown source".

#### `source-context` (for hardcoded sub-media)

When a CLI extracts `text.hardcoded` strings — strings embedded in
script files or binary resources — it MUST also capture the source
context: the surrounding lines of code so a translator can read the
actual usage.

Example:

```text
# Hardcoded string in scenes/day1/scene_001.rpy:42

 41 │     if player.gender == "male":
 42 │         narrator("Hello {player}.")
 43 │     else:
 44 │         narrator("Hello {playeress}.")
```

The string `"Hello {player}."` is extracted, and its source-context
captures lines 41–43 (3 lines of context as configured). The
captured block goes into the translation unit as a comment or
context field.

XLIFF representation:

```xml
<trans-unit id="tu-0042" original-file="scenes/day1/scene_001.rpy">
  <source>Hello {player}.</source>
  <target>你好 {player}。</target>
  <context-group name="source-context" purpose="information">
    <context context-type="sourcefile">scenes/day1/scene_001.rpy</context>
    <context context-type="linenumber">42</context>
    <context context-type="snippet">
41 │     if player.gender == "male":
42 │         narrator("Hello {player}.")
43 │     else:</context>
  </context-group>
</trans-unit>
```

PO representation:

```po
#: scenes/day1/scene_001.rpy:41
#: scenes/day1/scene_001.rpy:42
msgid "Hello {player}."
msgstr "你好 {player}。"
```

JSON representation (engine-defined):

```json
{
  "id": "tu-0042",
  "source": "Hello {player}.",
  "target": "你好 {player}。",
  "context": {
    "original_file": "scenes/day1/scene_001.rpy",
    "line": 42,
    "snippet": "41 │     if player.gender == \"male\":\n42 │         narrator(\"Hello {player}.\")\n43 │     else:"
  }
}
```

#### `location`

For positional information the CLI knows (XLIFF calls this
`<context context-type="linenumber">`; PO uses `file:line`). When
unknown, the field is omitted.

#### `engine_path`

Engine-internal logical path. Engine-defined; CLI passes it through.
When omitted, OmegaT falls back to `original-file`.

### `image` / `audio` / `video`

```yaml
image:
  layout: sub_media_dirs    # sub_media_dirs | flat
  sidecar: yaml            # engine-defined sidecar format (optional)

audio:
  layout: sub_media_dirs
  manifest: ./audio/manifest.yaml

video:
  layout: sub_media_dirs
  reencode: false          # if true, CLI may re-encode on extract
```

The fields here are convention hints. Engines MAY ignore any of them.
The full semantics are in
[12-file-structure.md](./12-file-structure.md).

### Engine-extension media

For each engine-extension media identifier, the same block shape
applies:

```yaml
font:
  layout: sub_media_dirs
  manifest: ./font/manifest.yaml
```

When the engine exposes `font` as a sub-media of an existing media,
the configuration goes under that parent (see [04-media.md § Sub-Media](./04-media.md#sub-media)).

---

## 5.9 `engine`

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

## 5.10 Reserved top-level keys

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

## 5.11 Path resolution

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