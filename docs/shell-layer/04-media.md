# 04. Media

> Status: **Normative**. Defines the standard media identifiers, the
> rules for adding engine-extension media, and the Sub-Media
> sub-categorization mechanism.

---

## 4.1 Standard media

Two media are **standard**: every gallate CLI MUST be able to declare
support for them, and a Wrapper MAY assume they are baseline.

| Flag | Name    | Description                                |
| ---- | ------- | ------------------------------------------ |
| `-t` | `text`  | Text, localized strings, text resources    |
| `-i` | `image` | Images, textures, illustrations, etc.     |

`text` and `image` are the **standard baseline**. A pure-text engine
might omit `image`; a no-text engine is not a valid gallate CLI.

---

## 4.2 Engine-extension media

Audio, video, fonts, and any other resource kind beyond text/image
are **engine-extension media**. The CLI defines them; the standard
spec does not require any engine to implement them.

Examples:

```text
audio
  voice      # voice acting
  bgm      # background music
  sfx      # sound effects

video
  cutscene   # in-game cutscenes
  cinematic  # cinematic camera
  opening    # opening / ending

font         # fonts (TTF, OTF, glyph tables)
```

When the engine exposes these, they get the same flag treatment on
the Shell layer:

```text
-a          = audio (the engine decides whether to expose a single
              audio media or audio sub-media; see 4.3)
-v          = video
--engine.font=...      # font typically isn't a media flag; see below
```

### Rules

1. The extension media identifier MUST use the engine namespace —
   bare `font` for the single-engine CLI, or `artemis.font` etc.
   when sharing an engine name across CLIs.
2. The CLI MUST declare each extension media in its
   `manifest` / `features` document so Wrapper knows about it.
3. The standard CLI MUST NOT recognize any extension media the
   engine hasn't declared.
4. Engines MAY or MAY NOT expose `-a` / `-v` flags for audio/video.
   When not exposed, the engine sub-media are accessible only via
   the `--engine.*.includes` Sub-Media mechanism (see 4.3).
5. `font` is typically handled as an engine option (`--engine.font=…`)
   rather than a media flag, because it is usually processed
   alongside text. Engines MAY still treat it as a media if their
   architecture calls for it.

### Why audio / video are not standard

Most game engines ship with text and image assets. Audio, video, and
fonts vary wildly: an ASCII adventure has none of them; a visual
novel has voice but no video; a 3D RPG has all three plus font
glyphs. Forcing all CLIs to advertise four media classes when
two-thirds of engines lack one or more would be dishonest. Treating
text/image as standard and the rest as extensions lets each CLI
declare exactly what it supports without contortion.

---

## 4.3 Sub-Media

A CLI MAY define **sub-media** under any media — standard or
extension. Sub-media distinguishes different *kinds* of the same
resource type.

Examples:

```text
text
  ├── dialog       # conversation text
  ├── menu         # menu options
  └── hardcoded    # strings embedded in scripts or binaries

image
  ├── background   # background art
  ├── portrait     # character portraits
  ├── portrait_diff  # portrait diffs (em expression, pose)
  └── ui           # UI textures

audio
  ├── voice        # voice acting
  ├── bgm          # background music
  └── sfx          # sound effects

video
  ├── cutscene     # in-engine cutscenes
  ├── cinematic    # cinematic camera
  └── opening      # openings / endings
```

### Shell form

```bash
# Include (whitelist) — only the listed sub-media are processed
tool -et ./gallate.yaml \
  --engine.text.includes=hardcoded

tool -ei ./gallate.yaml \
  --engine.image.includes=portrait_diff

tool -ea ./gallate.yaml \
  --engine.audio.includes=voice,bgm

# Exclude (subtractive) — remove from the includes set
tool -ei ./gallate.yaml \
  --engine.image.includes=portrait \
  --engine.image.excludes=portrait_diff
```

### YAML form (`gallate.yaml`)

```yaml
engine:
  text:
    includes:
      - dialog
      - menu
      - hardcoded
    excludes:
      - debug_log

  image:
    includes:
      - background
      - portrait
      - portrait_diff
      - ui
    excludes:
      - ui

  audio:
    includes:
      - voice
      - bgm
      - sfx
    excludes:
      - sfx

  video:
    includes:
      - cutscene
      - cinematic
      - opening
```

### Rules

1. Sub-media identifiers MUST be declared by the engine (in
   `manifest` / `features` / a Sub-Media discovery command).
2. Undeclared sub-media is illegal; CLI MUST reject it.
3. `includes` is a whitelist: unlisted sub-media are not processed.
4. `excludes` is subtractive: it removes from the includes set.
5. An item in `excludes` that is not in `includes` is an error
   (catches misconfiguration early).
6. Extension media (e.g. `font`) may also declare sub-media with
   the same syntax.
7. Sub-media MUST NOT replace the standard media semantics — `t`
   still means "any text", not "specific text sub-type".

---

## 4.4 Default media

When no media flag is given:

```bash
tool -e ./gallate.yaml
```

The CLI uses the project's `media:` list:

```yaml
# gallate.yaml
media:
  - text
  - image
```

Then:

```bash
tool -e ./gallate.yaml
```

is equivalent to:

```bash
tool -eti ./gallate.yaml
```

If `media:` is absent, the engine default is used (engine-specific;
not standardized).

---

## 4.5 CLI media override

When media flags are given explicitly, they **completely override**
the YAML media list — not merge.

```yaml
# gallate.yaml
media:
  - text
  - image
```

```bash
tool -ea ./gallate.yaml
```

Process only `audio` (assuming this engine has declared audio support
and exposed `-a`). The `text` and `image` defaults are ignored for
this invocation.

A CLI that does NOT expose `-a` rejects `-ea` with exit code 2
(invalid CLI usage) before consulting `gallate.yaml`.

---

## 4.6 Engine-trimming media

An engine is not required to support every media it has declared.
A pure-text engine, for example, declares only `text`; a visual novel
declares `text` + `image` + `audio` but no `video`. The engine
documents the supported subset in its
[Protocol-layer features](../protocol/03-discovery.md#features)
document:

```yaml
resources:
  text: true
  image: true
  audio: true
  video: false
```

When the user invokes a media the engine doesn't support:

```bash
artemis-tool -ev ./gallate.yaml
```

The CLI MUST report it as an error (NOT silently skip):

```text
Error: media 'video' is not supported by this engine.
```

Exit code: 6 (`Unsupported Media`).

The flag letters keep their identities (`-a` for audio, `-v` for
video, etc., when the engine chose to expose them). When the engine
chose NOT to expose them at the Shell layer, the flag is simply not
present in `tool --help`.