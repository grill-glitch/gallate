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

  text/       per-translation-unit files (XLIFF / PO / JSON / …)
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
│   ├── scenes_intro.yaml
│   ├── scenes_day1_scene_001.xlf
│   ├── scenes_day1_scene_002.xlf
│   └── …
└── reports/               # optional: validation findings, glossary dumps
    └── validation.yaml
```

CLI MAY flatten `units/` so files land directly under `text/`. The
default is `text/units/` so XLIFF files don't pollute the directory
listing of a human browsing the project by hand.

### Naming convention

The recommended file name shape is:

```text
<media-resource-path>.<translation-format-extension>
```

Examples:

```text
scenes/intro.bin            →  text/units/scenes_intro.xlf
scenes/day1/scene_001.bin   →  text/units/scenes_day1_scene_001.xlf
fonts/ascii.glyph_table     →  text/units/fonts_ascii_glyph_table.xlf
```

The CLI substitutes `/` with `_` so a flat directory listing stays
readable. Engines MAY use a deeper layout (mirror of the input
directory) — see [12.3 Layout modes](#123-layout-modes).

### `text/manifest.yaml`

A CLI MAY emit this file at the end of an extract run. It records
what was extracted and when:

```yaml
extracted_at: 2026-09-09T12:34:56Z
cli:
  id: artemis
  version: 1.2.0
  protocol: gcwp-1.0
counts:
  files_scanned: 1524
  files_matched: 318
  strings_extracted: 8421
  by_sub_media:
    dialog: 6320
    menu: 480
    hardcoded: 1621
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
  #   flat     — text/units/<path-with-_>.xlf
  #   mirror   — text/units/<engine-path>/<file>.xlf
  #   single   — text/translation.xlf  (all units in one file)
```

| Mode | Pros | Cons |
| ---- | ---- | ---- |
| `flat`   | Easy git diffs across files. Easy partial commits. | Naming collisions when two source paths only differ by `/`. |
| `mirror` | 1:1 mapping to source; no collisions. | Deep directory trees; harder to spot duplicates. |
| `single` | One file per format — OmegaT opens one XLIFF. | One huge file; partial review impossible; merge conflicts guaranteed. |

### `flat` (default)

```text
text/units/
├── scenes_intro.xlf
├── scenes_day1_scene_001.xlf
├── scenes_day1_scene_002.xlf
└── fonts_ascii_glyph_table.xlf
```

### `mirror`

```text
text/units/
├── scenes/
│   ├── intro.xlf
│   └── day1/
│       ├── scene_001.xlf
│       └── scene_002.xlf
└── fonts/
    └── ascii/
        └── glyph_table.xlf
```

### `single`

```text
text/
└── translation.xlf       # all translation units in one document
```

---

## 12.4 Per-format details

### XLIFF (`.xlf` / `.xliff`)

Standard XLIFF 1.2 with `<file>` and `<trans-unit>` elements. See
[05-config-file.md § text: format](./05-config-file.md#text-format)
for the metadata fields each `<trans-unit>` carries
(`original-file`, `source-context`, …).

### PO (`.po`)

GNU gettext. One file per logical domain. Naming:

```text
text/units/<domain>.po
```

Engine MAY group multiple domains:

```text
text/units/main.po
text/units/help.po
```

### JSON (`.json`)

Arbitrary engine-defined structure. Standard keys:

```yaml
schema:
  units:
    - id:        # unique string id
      source:    # source text
      target:    # translated text (empty pre-translation)
      context:   # optional, engine-defined
      meta:      # optional, freeform engine-defined metadata
```

The CLI MUST document the exact JSON shape in its engine extension
section. The schema above is the minimum that Wrapper / OmegaT will
reliably handle.

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
`audio/manifest.yaml` listing duration / format / voice actor.

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

- The exact XLIFF schema inside each file (engine-defined, validated
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
text/manifest.yaml          # if present
text/units/*.xlf            # or wherever the engine placed them
```

The Wrapper does not need to guess. It uses the manifest when
present, falls back to glob otherwise. Engine wrappers MAY add an
`engine.manifest_path` hint:

```yaml
engine:
  manifest_path: ./text/manifest.yaml
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
| `text/`        | `text/units/*.xlf`        | n/a (units inside files) |
| `image/`       | `image/<sub-media>/*`    | yes |
| `audio/`       | `audio/<sub-media>/*`    | yes |
| `video/`       | `video/<sub-media>/*`    | yes |
| `font/` (ext.) | `font/<sub-media>/*`      | yes |

All paths resolve relative to the Project Root. CLI MUST be
deterministic — same input, same output paths, modulo file
timestamps.