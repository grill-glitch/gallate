# 12. File Structure

> Status: **Normative**. Defines how files inside the standard media
> directories (`text/`, `image/`, `audio/`, `video/`, …) are named,
> organized, and structured.

The [06-project-structure.md](./06-project-structure.md) chapter
covers **which directories** exist at the Project Root. This chapter
covers **what lives inside them**.

---

## 12.1 Convention over rule

The CLI decides the in-directory layout. This chapter is a
**recommended convention**, not a contract — engines MAY diverge,
but doing so forfeits the `gallate-standard-layout` label and the
ability to share tooling across engines.

```text
Standard media directories:

  text/       per-translation-unit files (JSON / …)
  image/      per-image files
  audio/      per-audio-clip files
  video/      per-video files
```

---

## 12.2 `text/`

### Top-level layout

```text
text/
├── manifest.yaml          # optional: what was extracted, when, by which CLI
├── units/                 # per-translation-unit files (default location)
│   ├── scenes_intro.json
│   ├── scenes_day1_scene_001.json
│   ├── scenes_day1_scene_002.json
│   └── …
└── reports/               # optional: validation findings, glossary dumps
    └── validation.yaml
```

CLI MAY flatten `units/` so files land directly under `text/`. The
default is `text/units/` so unit files don't pollute the directory
listing of a human browsing the project by hand.

### Naming convention

The recommended file name shape is:

```text
<media-resource-path>.<translation-format-extension>
```

Examples:

```text
scenes/intro.bin            →  text/units/scenes_intro.json
scenes/day1/scene_001.bin   →  text/units/scenes_day1_scene_001.json
fonts/ascii.glyph_table     →  text/units/fonts_ascii_glyph_table.json
```

The CLI substitutes `/` with `_` so a flat directory listing stays
readable. Engines MAY use a deeper layout (mirror of the input
directory) — see [12.3 Layout modes](#123-layout-modes).

### `text/manifest.json`

A CLI MAY emit this file at the end of an extract run. It records
what was extracted and when:

```json
{
  "extracted_at": "2026-09-09T12:34:56Z",
  "cli": {
    "id": "artemis",
    "version": "1.2.0",
    "protocol": "gcwp-1.0"
  },
  "counts": {
    "files_scanned": 1524,
    "files_matched": 318,
    "strings_extracted": 8421,
    "by_sub_media": {
      "dialog": 6320,
      "menu": 480,
      "hardcoded": 1621
    }
  }
}
```

This file is OPTIONAL. Wrapper / OmegaT MAY use it for project
dashboards but MUST NOT depend on it.

---

## 12.3 Layout modes

A CLI MAY pick one of three layouts. The choice is documented in
`gallate.yaml`:

```yaml
text:
  layout: flat              # default
  # alternatives:
  #   flat     — text/units/<path-with-_>.json
  #   mirror   — text/units/<engine-path>/<file>.json
  #   single   — text/translation.json  (all units in one file)
```

| Mode | Pros | Cons |
| ---- | ---- | ---- |
| `flat`   | Easy git diffs across files. Easy partial commits. | Naming collisions when two source paths only differ by `/`. |
| `mirror` | 1:1 mapping to source; no collisions. | Deep directory trees; harder to spot duplicates. |
| `single` | One document — OmegaT opens a single file. | One huge file; partial review impossible; merge conflicts guaranteed. |

### `flat` (default)

```text
text/units/
├── scenes_intro.json
├── scenes_day1_scene_001.json
├── scenes_day1_scene_002.json
└── fonts_ascii_glyph_table.json
```

### `mirror`

```text
text/units/
├── scenes/
│   ├── intro.json
│   └── day1/
│       ├── scene_001.json
│       └── scene_002.json
└── fonts/
    └── ascii/
        └── glyph_table.json
```

### `single`

```text
text/
└── translation.json      # all translation units in one document
```

---

## 12.4 Unit file format (`gallate.translation` v1)

JSON is the only standard unit-file format. XLIFF and PO are **not**
standard formats; an engine that needs one MAY expose it as an
engine-extension format, but Wrapper / OmegaT are not required to
handle anything other than JSON.

The unit-file format is the canonical **translation state** for a
gallate project. It is a working file, not a database. See
[§12.13 Design principle](#1213-design-principle) for the rule that
governs every field below.

### 12.4.1 Container

```json
{
  "format": "gallate.translation",
  "version": 1,
  "source": "ja",
  "target": "zh-CN",
  "entries": []
}
```

`entries[]` is a flat array; the container may be empty (just-extracted,
no strings found) or carry thousands of entries. The example above
shows the empty case; see the next subsection for a populated one.

| Key | Required | Meaning |
| --- | --- | --- |
| `format` | yes | Literal `"gallate.translation"`. Identifies the file kind. |
| `version` | yes | Format version. v1 is documented here. The CLI refuses to load a file whose `version` is higher than it knows. |
| `source` | yes | BCP-47 source language tag (`ja`, `en-US`, …). |
| `target` | yes | BCP-47 target language tag. |
| `entries[]` | yes | Translation entries, one per extractable string. |

The container itself is **language-agnostic** — neither `entries[].source` nor `entries[].target` carries a language tag. The language pair lives at the document level because every entry in the document is, by construction, a `(source, target)` pair under the same pair.

### 12.4.2 Entry

```json
{
  "id": "scenario/0083_SS_01_x.lua:L0142",
  "source": "今日はいい天気ですね。",
  "target": "今天天气真好呢。",
  "state": "translated",

  "source_context": {
    "file": "scenario/0083_SS_01_x.lua",
    "line": 142,
    "end_line": 144,
    "snippet": "141 │ if FLAG(\"opening\") then\n142 │     COMMAND(\"セリフ\", \"アキト\", \"…どうしたの？\")\n143 │ end"
  },

  "context": {
    "speaker": "Alice",
    "scene": "0083_SS_01",
    "location": "school"
  },

  "placeholders": [
    {"id": "player", "syntax": "{player}", "type": "variable"}
  ],

  "notes": [
    {"text": "角色第一次登场。", "author": "translator"}
  ],

  "provenance": {"type": "human"},

  "metadata": {}
}
```

| Key | Required | Default | Kind | Meaning |
| --- | --- | --- | --- | --- |
| `id` | yes | — | derived | Position-derived identity. See [05-config-file.md § `id`](./05-config-file.md#id-position-derived). |
| `source` | yes | — | derived | Source text. Re-extractable. |
| `target` | yes | `""` | authored | Translated text. Empty before translation. The only field that is genuinely human/AI authored. |
| `state` | yes | `"initial"` | authored | Current state label. See [05-config-file.md § `state`](./05-config-file.md#state). |
| `source_context` | optional | sentinels | derived | Four-field record (`file` / `line` / `end_line` / `snippet`). Re-captured at extract time, preserved across inject. See [05-config-file.md § `source_context`](./05-config-file.md#source_context). |
| `context` | optional | `{}` | authored | Free-form translator-helper data (`speaker` / `scene` / `location` / …). See [05-config-file.md § `context`](./05-config-file.md#context). |
| `placeholders` | optional | `[]` | derived | Placeholders detected in `source`. CLI uses this to validate that `target` preserves them. See [05-config-file.md § `placeholders`](./05-config-file.md#placeholders). |
| `notes` | optional | `[]` | authored | Translator / reviewer notes. See [05-config-file.md § `notes`](./05-config-file.md#notes). |
| `provenance` | optional | `{"type": "human"}` | authored | Where the current `target` came from. See [05-config-file.md § `provenance`](./05-config-file.md#provenance). |
| `metadata` | optional | `{}` | engine | Engine-defined extension namespace. See [05-config-file.md § `metadata`](./05-config-file.md#metadata). |

The **Kind** column is normative:

- **derived** — the CLI MUST be able to recompute the field from the
  source resource alone. Persisting it is a cache; missing it after
  re-extraction is not an error.
- **authored** — a human or AI wrote it. The CLI MUST NOT recompute
  or silently overwrite it on re-extraction.
- **engine** — engine-defined semantics. The CLI MAY add / read it
  under the engine's own contract; the spec does not interpret it.

### 12.4.3 Multiple-file layout

One file per logical domain (in the standard layouts, one per source
resource). Naming:

```text
text/units/<domain>.json
```

Engine MAY group multiple domains:

```text
text/units/main.json
text/units/help.json
```

The CLI MUST document any extra keys it emits in its engine
extension section. The shape above is the minimum that Wrapper /
OmegaT will reliably handle.

---

## 12.5 `image/`

```text
image/
├── bg/
│   └── scenes_day1_scene_001_bg.png
├── portrait/
│   └── character_alice_default.png
├── portrait_diff/
│   └── character_alice_smile.png.json     # placeholder file for diff
└── ui/
    └── button_save.png
```

Sub-Media directories (`bg/`, `portrait/`, …) mirror the Sub-Media
identifier in the CLI invocation:

```yaml
image:
  sub_media_dirs: true
```

When `false`, all sub-media flatten into `image/`. Default: `true`.

`portrait_diff` files do not replace the source portrait — they are
side-by-side deltas. The `.json` placeholder records the base image
and the regions that differ:

```json
{
  "base": "character_alice_default.png",
  "diff": {
    "region": [120, 80, 240, 320],
    "kind": "expression_smile"
  }
}
```

This shape is engine-defined; the above is one example.

---

## 12.6 `audio/`

```text
audio/
├── voice/
│   ├── scene_001_line_001.wav
│   └── scene_001_line_002.wav
├── bgm/
│   └── title_theme.ogg
└── sfx/
    └── ui_click.ogg
```

Same sub-media-directory rule as `image/`. CLI MAY also emit a side
`audio/manifest.json` listing duration / format / voice actor.

---

## 12.7 `video/`

```text
video/
├── cutscene/
│   └── intro.mp4
├── cinematic/
│   └── trailer_e3.mp4
└── opening/
    └── op_credits.webm
```

Same sub-media-directory rule. Videos are typically large; the
Wrapper SHOULD NOT re-encode, only re-mux (replace audio track) when
possible.

---

## 12.8 Engine-extension directories

When the engine exposes audio/video/font, the corresponding directories
follow the same conventions as above:

```text
font/
├── ascii/
│   └── font_ascii_8x16.fnt
└── cjk/
    └── font_cjk_notosans.fnt
```

`font/` entries are typically NOT translation targets (they are
binary), so the CLI only emits them when the engine has explicit
"localize font" semantics. See
[04-media.md § Engine-extension media](./04-media.md#engine-extension-media).

---

## 12.9 What the standard does NOT mandate

- The exact JSON shape inside each file (engine-defined, validated
  only by the engine).
- Whether the CLI produces a per-resource file (preferred) or a
  single consolidated file.
- Whether sub-media directories are mirrored or flattened.
- Whether the manifest file is generated.
- Whether `reports/` is generated.

These are implementation choices the engine wrapper documents. The
Shell layer only mandates that:

- The standard media directories exist where the project's media
  type applies.
- Path resolution is consistent across runs (the same input
  produces the same output path).
- File names are stable across runs so git diffs and OmegaT
  references don't break.

---

## 12.10 Discoverability

A Wrapper can introspect a project by reading:

```text
text/manifest.json          # if present
text/units/*.json           # or wherever the engine placed them
```

The Wrapper does not need to guess. It uses the manifest when
present, falls back to glob otherwise. Engine wrappers MAY add an
`engine.manifest_path` hint:

```yaml
engine:
  manifest_path: ./text/manifest.json
```

Standard CLI ignores this; the Wrapper uses it when present.

---

## 12.11 Working directory inside media files

Scripts in `scripts/pre` and `scripts/post` see the standard media
directories at the Project Root. They MAY modify files in place
(e.g. normalize encoding) before the engine reads them. The CLI does
NOT assume any post-processing happened — it reads raw bytes.

---

## 12.12 Summary

| Directory | Default mode | Sub-Media dirs? |
| --- | --- | --- |
| `text/`        | `text/units/*.json`       | n/a (units inside files) |
| `image/`       | `image/<sub-media>/*`    | yes |
| `audio/`       | `audio/<sub-media>/*`    | yes |
| `video/`       | `video/<sub-media>/*`    | yes |
| `font/` (ext.) | `font/<sub-media>/*`      | yes |

All paths resolve relative to the Project Root. CLI MUST be
deterministic — same input, same output paths, modulo file
timestamps.

---

## 12.13 Design principle

Every field on `entries[]` follows one rule:

> **Source is derived. Identity is derived. Translation is
> authored. Notes are authored. Provenance is authored. Engine
> metadata is engine-defined.**

A field is **derived** if the CLI can recompute it from the source
resource: `source`, `id`, `source_context`, `placeholders`. These
are caches. The CLI is free to discard and re-extract them; a
Wrapper MUST be able to regenerate them by re-running extract.

A field is **authored** if a human or an AI wrote it: `target`,
`state`, `context` (when populated by a translator), `notes`,
`provenance`. The CLI MUST NOT silently recompute or overwrite
authored fields on re-extraction.

A field is **engine** when the engine defines its semantics
(`metadata`, plus engine-defined extensions). The spec does not
interpret engine fields.

The consequence:

```text
source resource
       │
       ▼
  Gallate CLI extract
       │
       ▼
  text/units/*.json   ← derived fields recomputed; authored preserved
       │
       ▼
  human / AI / editor   (mutates only authored fields)
       │
       ▼
  Gallate CLI inject
```

`text/units/*.json` is **disposable**. Deleting the file and
re-running extract loses no authored work — the CLI re-derives the
derived fields, finds the matching source, and the next inject
re-walks the entries. (In practice a Wrapper keeps the file
because re-typing every `target` is expensive, but the spec does
not depend on that.)

The CLI does not need a UUID registry, a translation-memory
database, or an `id → unit` map. The `id` is recomputable. The
`source` is recomputable. The authored fields are git diffs.
