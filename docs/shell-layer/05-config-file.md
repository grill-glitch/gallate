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
  format: json
  layout: flat
  metadata:
    original_file: true
    source_context: true
    location: true
    placeholders: true
    engine_path: true
  hardcoded:
    context_lines: 3
    max_bytes: 4096
    engine_extensions:
      - .py
      - .lua
      - .rpy
      - .ks
  lifecycle:
    written_on: extract
    read_on:
      - post-extract
      - pre-inject
  meta:
    original_file:  original_file
    source_context: source_context
    location:       location
    placeholders:   placeholders
    engine_path:    engine_path

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
  format: json             # json | engine-extension
  layout: flat             # flat | mirror | single (see 12-file-structure.md)
  sub_media_dirs: false    # ignored (sub-media live inside files for text)

  # Whether to emit each metadata field on a translation unit.
  # All default to true. The data shape itself is fixed by this
  # spec; these flags only turn emission on or off.
  metadata:
    original_file: true        # source path inside the game archive
    source_context: true       # four-field record for text.hardcoded
    location: true             # line / offset / length (non-hardcoded units)
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

  # When each metadata field is written and read.
  # Defaults match the standard workflow; both fields are optional.
  # The block is OPTIONAL entirely — when omitted, behavior matches
  # the defaults below.
  lifecycle:
    written_on: extract     # extract | never
                            #   extract (default): CLI writes metadata
                            #     during extract and preserves it during
                            #     inject. The source code does not change
                            #     between extract and inject, so there is
                            #     no reason for the CLI to re-capture.
                            #   never: metadata is never written (overrides
                            #     every metadata.* flag).
    read_on:                 # when the Wrapper / OmegaT reads it
      - post-extract         #   right after extract: shown to translator
      - pre-inject           #   right before inject: QA review
                             #   The build phase MUST NOT read source-context.
```

#### Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `format` | enum | Output format. Standard: `json`. |
| `layout` | enum | File layout. Standard: `flat` / `mirror` / `single`. See [12-file-structure.md](./12-file-structure.md). |
|| `metadata.original_file` | bool | If true, every entry carries an `original_file` key naming the source resource path inside the game archive. Default: `true`. |
|| `metadata.source_context` | bool | If true, every `text.hardcoded` entry carries the four-field `source_context` record (`file` / `line` / `end_line` / `snippet`) described in the [`source_context`](#source_context) subsection below. Default: `true`. |
|| `metadata.location` | bool | If true, non-hardcoded entries carry `line` / `offset` / `length` of the source string inside its file. Default: `true`. For `text.hardcoded` entries, position is in `source_context` instead. |
|| `metadata.placeholders` | bool | If true, entries carry the auto-detected `placeholders[]` list. Default: `true`. |
|| `metadata.engine_path` | bool | If true, entries carry the engine-internal logical path (engine-defined). Default: `true`. |
|| `hardcoded.context_lines` | int | Lines of surrounding code to capture for `text.hardcoded` entries. Default: `3`. |
|| `hardcoded.max_bytes` | int | Upper bound on the captured context payload, per entry. Default: `4096`. |
|| `hardcoded.engine_extensions` | list | File extensions the engine treats as code for context capture. Empty list = engine decides. |
|| `lifecycle.written_on` | enum | `extract` (default) or `never`. The CLI writes the metadata only during extract and preserves it across inject. The build phase never writes metadata. |
|| `lifecycle.read_on` | list | Phases when Wrapper / OmegaT should surface the metadata. Default: `post-extract` and `pre-inject`. The `build` phase MUST NOT read `source_context`. |

#### `meta:` (optional mappings)

```yaml
text:
  meta:
    # Optional: declare which JSON key each metadata field lands
    # under. Without this block, the spec's defaults apply.
    # This block is purely a MAPPING declaration — it does NOT
    # change the data shape, only the output keys.
    # The five values below are also the spec's default key names.
    original_file:  original_file      # entry-level JSON key
    source_context: source_context     # entry-level JSON object
    location:       location           # entry-level JSON object
    placeholders:   placeholders       # entry-level JSON array
    engine_path:    engine_path        # entry-level JSON key
```

The `meta:` block is **purely declarative** — it tells the CLI which
output keys the spec-mandated data shape uses. It MUST NOT add,
rename, or remove fields. The data shape (`file` / `line` /
`end_line` / `snippet` for `source_context`) is fixed by this spec
and is not negotiable.

Engines MAY define engine-extension media with their own `meta:`
block. The keys are engine-defined; the constraint is the same
(no shape mutation, only key mapping).

#### `id` (position-derived)

Every translation entry has an `id`. The `id` MUST be **derived from
the entry's position in its source file**, not from an
extraction-order counter. A counter renumbers every entry after an
insertion, silently invalidating translation memory; a positional
id survives re-extraction unchanged.

Shape:

```text
<resource-path>:L<line>
```

| Part | Rule |
| --- | --- |
| `<resource-path>` | The source resource path inside the game archive (e.g. `scenario/0083_SS_01_x.lua`). Engine-defined. The CLI MUST use the full path — basename alone is not enough, because two source files can share a basename. |
| `L` | Literal, uppercase. Marks the following number as a line. |
| `<line>` | 1-based line number, zero-padded to **at least** 4 digits (`L0142`). Lines beyond 9999 use as many digits as needed (`L12345`). |
| `#<n>` | Disambiguation suffix for the second and later entry on the same line, counted in source order, starting at `2` (`…#2`, `…#3`). Omitted for the first entry on a line. |

Example:

```text
scenario/0083_SS_01_x.lua:L0142        first entry on line 142
scenario/0083_SS_01_x.lua:L0142#2      second entry on the same line
```

Rules:

- The CLI MUST NOT use a run-order counter (`tu-0001`, `U000001`) as
  the entry `id`. Such ids are not stable across re-extraction.
- The `id` MUST be stable as long as the source file is unchanged.
- When the position is unknown (binary blob, obfuscated bytecode),
  `line` takes the sentinel `0` and the entries of that file are
  ordered `…#1`, `#2`, … by a deterministic engine-defined order.
- The `id` MUST be unique within the containing output document.
  The full resource path makes this trivial in practice; the `#<n>`
  suffix handles the remaining "two strings on the same line" case.

#### `state`

A **current label**, not a state machine. The label tells Wrapper /
OmegaT how the `target` was produced and what confidence to give it.

| Value | Meaning |
| --- | --- |
| `initial` | `target` is empty or untouched. The CLI sets this on extract. |
| `translated` | `target` was filled in (by a human, an AI, or a previous translation-memory import). |
| `reviewed` | A human reviewer has confirmed the `target`. |
| `final` | QA passed. |
| `needs_review` | Source changed after `final`/`reviewed`, OR validation rejected the `target`. Reverts are normal and expected. |

Rules:

- Labels MUST be reversible. A `final` entry MUST be allowed to drop
  to `needs_review` if the source changes; the CLI MUST NOT throw.
- The CLI MUST NOT enforce a state machine. `translated` → `final`
  with no `reviewed` is allowed.
- The CLI extracts with `state: "initial"` (or whatever the
  previous value of the field is, if the entry already exists and
  has a non-empty `target`).
- `state` is **authored** — the CLI MUST NOT silently rewrite it on
  re-extraction.

#### `source`

The source text. Re-extractable from the source resource.

#### `target`

The translated text. The only field that is genuinely human/AI
authored. Empty before translation. The CLI MUST NOT silently
overwrite it on re-extraction.

#### `source_context` (for hardcoded sub-media)

> ⚠ **Normative data model.** The CLI MUST capture source context
> for every `text.hardcoded` entry as a fixed data model. The JSON
> output is only a serialization — the Wrapper / OmegaT reads the
> same four fields regardless of format.

**When is `source_context` written?**

Source code is read only at **extract** time. The CLI captures
the four-field record there and embeds it in the entry. At
**inject** time, the CLI reads the translation; it does not
re-capture source code (it is not changing). The captured
`source_context` MUST be preserved verbatim through any number of
extract → inject cycles.

**When is `source_context` read?**

Wrapper / OmegaT should surface `source_context` to the translator
right after extract (`post-extract`), and to QA right before inject
(`pre-inject`). The **build** phase MUST NOT read `source_context`
— the engine already knows the code; the captured snippet is for
human consumption only.

These phases are controlled by `lifecycle.read_on` (see above).
The default covers the two intended consumers; the build phase
is intentionally excluded.

**Data model**

When a CLI extracts `text.hardcoded` strings — strings embedded in
script files or binary resources — it captures the source context as
a **four-field record**:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `file` | path | yes | Source path of the file the string lives in. Same as `original_file` for the entry. |
| `line` | int | yes | 1-based line number where the string lives. |
| `end_line` | int | yes | 1-based last line number of the captured snippet. Equals `line` for single-line strings. |
| `snippet` | string | yes | The captured source lines, joined with `\n`. Leading line number prefixes are optional but recommended. |

`snippet` length is bounded by `hardcoded.max_bytes` (default 4096).
The CLI MUST truncate to the byte limit if needed, but MUST keep the
first line (the one containing the string) intact.

##### Example data model

The string `"……どうしたの？"` in `scenario/0083_SS_01_x.lua:142` with
3 lines of context produces this record:

```yaml
source_context:
  file: scenario/0083_SS_01_x.lua
  line: 142
  end_line: 144
  snippet: |
    141 │ if FLAG("opening") then
    142 │     COMMAND("セリフ", "アキト", "……どうしたの？")
    143 │ end
```

##### Serialization (JSON)

JSON is the only standard output format, so there is exactly one
serialization. Wrapper / OmegaT converters MUST round-trip the
model without loss.

```json
{
  "id": "scenario/0083_SS_01_x.lua:L0142",
  "source": "……どうしたの？",
  "target": "……怎么了？",
  "state": "translated",
  "original_file": "scenario/0083_SS_01_x.lua",
  "location": {
    "line": 142,
    "offset": 29,
    "length": 7
  },
  "source_context": {
    "file": "scenario/0083_SS_01_x.lua",
    "line": 142,
    "end_line": 144,
    "snippet": "141 │ if FLAG(\"opening\") then\n142 │     COMMAND(\"セリフ\", \"アキト\", \"……どうしたの？\")\n143 │ end"
  }
}
```

The `source_context` keys MUST be exactly: `file`, `line`,
`end_line`, `snippet`. Additional keys are allowed but MUST NOT
replace any of the four.

The `id` is position-derived — see [`id`](#id-position-derived)
above. `scenario/0083_SS_01_x.lua:L0142` follows directly from
`source_context.file` + `source_context.line`.

##### When the engine cannot capture

When the engine cannot locate the string's source (binary blob,
obfuscated bytecode), the four fields collapse:

```yaml
source_context:
  file: <the resource file the string came from>
  line: 0
  end_line: 0
  snippet: ""
```

CLI MUST emit the four-field record with these sentinel values
rather than omitting the `source_context:` object. The entry `id`
follows the unknown-position rule in [`id`](#id-position-derived).

#### `context` (translator-helper, authored)

Free-form data the translator (or the engine) writes to make
the entry humanly understandable. **Not** the source-code
context — that lives in `source_context` (above) and is
**derived** from the source file. `context` here is the field
the translator reaches for to record "this is Alice's first
appearance" or "this line is read aloud in a school scene".

```json
{
  "context": {
    "speaker": "Alice",
    "scene": "0083_SS_01",
    "location": "school"
  }
}
```

Rules:

- The CLI MUST NOT add keys to `context` automatically. Any key
  in `context` is either translator-authored or engine-authored
  under the engine's own contract.
- The CLI MUST NOT delete keys from `context` on re-extraction.
  It is **authored** data; see
  [12-file-structure.md § Design principle](./12-file-structure.md#1213-design-principle).
Engines MAY define a sub-namespace
(`context.engine:artemis`) for engine-private notes
without colliding with translator notes.

#### `placeholders`

Detected placeholders inside `source`. The CLI scans the source
text at extract time and records each placeholder; inject then
checks that `target` carries the same placeholders in the same
order.

```json
{
  "placeholders": [
    {"id": "player",   "syntax": "{player}",   "type": "variable"},
    {"id": "score",    "syntax": "%d",         "type": "format"},
    {"id": "FADE_IN",  "syntax": "[FADE_IN_3]","type": "control"},
    {"id": "kanji",    "syntax": "{ruby:漢字|かんじ}", "type": "ruby"}
  ]
}
```

| `type` | Meaning |
| --- | --- |
| `variable` | Substitution variable: `{name}`, `${name}`, `<name>`. |
| `format` | printf-style positional: `%d`, `%1$s`. |
| `control` | Engine control code: `[FADE_IN_3]`, `[B]`. The `id` is the code's name; the `syntax` is the literal. |
| `ruby` | Ruby / furigana annotation: `{ruby:漢字|かんじ}`. |
| `engine` | Engine-defined placeholder. The CLI MAY add other `type` values it can identify. |

Rules:

- `id` MUST be unique within an entry's `placeholders[]`.
- The CLI MUST reject `target` whose placeholders differ in id
  set or order from `source`'s, at inject time. (Mismatches in
  `type` are warnings, not errors — a translator may legitimately
  upgrade `%d` to `{score:d}` if the engine accepts it.)
- `placeholders` is **derived**. The CLI MAY omit it on entries
  where it scanned nothing.

#### `notes`

Translator and reviewer notes, attached to the entry. Unlike
`context`, `notes` is a stack — every note has an author and a
text, and the order is preserved.

```json
{
  "notes": [
    {"text": "角色第一次登场，语调要轻快。", "author": "translator"},
    {"text": "原文「いい天気ですね」是感叹而不是疑问，译文已调整。", "author": "reviewer"}
  ]
}
```

| Key | Required | Meaning |
| --- | --- | --- |
| `text` | yes | The note body. Plain text. |
| `author` | yes | Free-form string: `translator` / `reviewer` / `ai` / `cli` / `editor:<name>`. Not an enum; new authors are allowed without a spec bump. |

`notes` is **authored** — the CLI MUST NOT delete, reorder, or
overwrite notes on re-extraction.

#### `provenance`

Where the current `target` came from. Wrapper / Editor shows
this as a small badge next to the `target` field.

```json
{
  "provenance": {"type": "human"}
}
```

```json
{
  "provenance": {"type": "machine", "model": "Qwen2.5-7B-Instruct", "method": "machine_translation"}
}
```

```json
{
  "provenance": {"type": "tm",      "match": "fuzzy", "score": 0.92, "source": "previous_project.xlf"}
}
```

| `type` | Required extras | Meaning |
| --- | --- | --- |
| `human` | — | `target` was written or confirmed by a human. |
| `machine` | `model`, optional `method` | `target` came from a machine-translation system. `method` distinguishes `machine_translation` / `llm` / `embeddings_kNN` / etc. |
| `tm` | `match`, `source`, optional `score` | `target` came from a translation memory. `match` is `exact` / `fuzzy` / `context`. |
| `mt+review` | inherits from `human` and one of the above | `target` was machine-translated, then a human edited it. The `provenance` value reflects the *current* `target`, so a human edit moves it to `mt+review` with the original machine info preserved. |

Rules:

- `provenance` is **authored**. The CLI MUST update it only when
  `target` itself changes through a documented path (e.g. a
  Wrapper's "accept machine translation" action).
- The CLI MUST NOT invent `model` / `score` values that the user
  did not produce.

#### `metadata`

Engine-defined extension namespace. Engines MAY write anything
under `metadata`. The spec does not interpret these keys.

```json
{
  "metadata": {
    "engine:artemis": { "engine_specific_key": "value" }
  }
}
```

> The literal `engine:artemis` above is illustrative; the real prefix is
> `engine:` followed by the CLI's `manifest.id`. The angle-bracketed
> placeholder `engine:<engine-id>` in the prose above is **not** valid
> JSON syntax and is shown as documentation shorthand.

The CLI MUST document the keys it writes. Two engines sharing
a project MUST NOT write to the same `metadata` sub-namespace.

#### `original_file`

The `original_file` key lets a translator know exactly which file
inside the game archive a translation entry came from. Without it,
"errors" or follow-up QA cannot trace a missing translation back to
its origin.

Example JSON entry:

```json
{
  "id": "scenario/day1/scene_001.bin:L0042",
  "source": "Hello {player}",
  "target": "你好 {player}",
  "original_file": "scenes/day1/scene_001.bin"
}
```

The CLI MUST emit `original_file` whenever the value is knowable.
When `metadata.original_file` is `false`, the CLI MAY omit it but
Wrapper / OmegaT SHOULD treat its absence as "unknown source".

`original_file` is written at **extract** (the source code is read
then) and **preserved** across inject (the source code has not
changed; the CLI does not re-read it).

#### `location`

Positional information the CLI knows — `line` / `offset` / `length`
of the source string inside its file. When unknown, the field is
omitted.

`location` is written at **extract** (source code is read then).
It is preserved across inject.

#### `engine_path`

Engine-internal logical path. Engine-defined; CLI passes it through.
When omitted, Wrapper falls back to `original_file`.

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