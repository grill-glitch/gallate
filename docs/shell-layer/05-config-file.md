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
| `metadata.source_context` | bool | If true, every `text.hardcoded` unit carries the four-field source-context record (`file` / `line` / `end_line` / `snippet`) described in the `source-context` subsection below. Default: `true`. |
| `metadata.location` | bool | If true, non-hardcoded units carry `line` / `offset` / `length` of the source string inside its file. Default: `true`. For `text.hardcoded` units, position is in `source-context` instead. |
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

> ⚠ **Normative data model.** The CLI MUST capture source context
> for every `text.hardcoded` unit as a fixed data model. The chosen
> output format (XLIFF / PO / JSON) is only a serialization — the
> Wrapper / OmegaT reads the same four fields regardless of format.

When a CLI extracts `text.hardcoded` strings — strings embedded in
script files or binary resources — it captures the source context as
a **four-field record**:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `file` | path | yes | Source path of the file the string lives in. Same as `original-file` for the unit. |
| `line` | int | yes | 1-based line number where the string lives. |
| `end_line` | int | yes | 1-based last line number of the captured snippet. Equals `line` for single-line strings. |
| `snippet` | string | yes | The captured source lines, joined with `\n`. Leading line number prefixes are optional but recommended. |

`snippet` length is bounded by `hardcoded.max_bytes` (default 4096).
The CLI MUST truncate to the byte limit if needed, but MUST keep the
first line (the one containing the string) intact.

##### Example data model

The string `"Hello {player}."` in `scenes/day1/scene_001.rpy:42`
with 3 lines of context produces this record:

```yaml
context:
  file: scenes/day1/scene_001.rpy
  line: 42
  end_line: 44
  snippet: |
    41 │     if player.gender == "male":
    42 │         narrator("Hello {player}.")
    43 │     else:
```

##### Serialization per format

The CLI MUST serialize the same four fields into the chosen format.
Wrapper / OmegaT converters MUST round-trip the model through
either format without loss.

**XLIFF** (`<trans-unit>`):

```xml
<trans-unit id="tu-0042" original-file="scenes/day1/scene_001.rpy">
  <source>Hello {player}.</source>
  <target>你好 {player}。</target>
  <context-group name="source-context" purpose="information">
    <context context-type="sourcefile">scenes/day1/scene_001.rpy</context>
    <context context-type="linenumber">42</context>
    <context context-type="endlinenumber">44</context>
    <context context-type="snippet">41 │     if player.gender == "male":
42 │         narrator("Hello {player}.")
43 │     else:</context>
  </context-group>
</trans-unit>
```

Required `context-type` keys: `sourcefile`, `linenumber`,
`endlinenumber`, `snippet`. CLI MAY emit additional `<context>`
siblings (e.g. `columnnumber`) but MUST NOT rename the four.

**PO** (`#:` reference comments):

```po
#: scenes/day1/scene_001.rpy:42
#: scenes/day1/scene_001.rpy:43
#: scenes/day1/scene_001.rpy:44
msgid "Hello {player}."
msgstr "你好 {player}。"
```

PO has no structured context fields; the four-field model collapses
to one `#: file:line` comment per captured line. The `file` field
is implied by the comment target; `line` and `end_line` are the
range covered by the comments. There is no room for `snippet` text
in PO — see "Lossy formats" below.

**JSON**:

```json
{
  "id": "tu-0042",
  "source": "Hello {player}.",
  "target": "你好 {player}。",
  "context": {
    "file": "scenes/day1/scene_001.rpy",
    "line": 42,
    "end_line": 44,
    "snippet": "41 │     if player.gender == \"male\":\n42 │         narrator(\"Hello {player}.\")\n43 │     else:"
  }
}
```

JSON keys MUST be exactly: `file`, `line`, `end_line`, `snippet`.
Additional keys are allowed but MUST NOT replace any of the four.

##### Lossy formats

PO is intentionally lossy: `snippet` text cannot be represented
inside standard PO. Wrapper / OmegaT SHOULD fall back to:

1. Parsing `#: file:N` comments to recover `file` and `line`/
   `end_line`.
2. Re-reading the source file at the captured line range to
   reconstruct `snippet` (the CLI does not need to embed it).

JSON is lossless. XLIFF is lossless.

The CLI MUST NOT pick a lossy format when the user requested a
lossless one. `text.format: po` is a deliberate loss-of-information
choice; `text.format: xliff` or `json` preserve all four fields.

##### When the engine cannot capture

When the engine cannot locate the string's source (binary blob,
obfuscated bytecode), the four fields collapse:

```yaml
context:
  file: <the resource file the string came from>
  line: 0
  end_line: 0
  snippet: ""
```

CLI MUST emit the four-field record with these sentinel values
rather than omitting the `context-group` / `context:` object.

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