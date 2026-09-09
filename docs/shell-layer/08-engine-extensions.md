# 08. Engine Extensions

> Status: **Normative**. Defines how a CLI extends the standard
> Shell-layer behavior without breaking it.

---

## 8.1 What is an engine extension

Anything a CLI adds beyond the standard Shell-layer behavior:

- New `--engine.*` options
- New media identifiers (audio, video, font, …)
- Sub-media under standard or extension media
- New operations beyond `-e` / `-i` (rare)

A compliant CLI MAY add any of these. It MUST do so under a clear
engine namespace and MUST NOT redefine standard behavior.

---

## 8.2 Naming convention

Engine-extension options use the `--engine.KEY[.SUBKEY]=VALUE` form:

```bash
artemis-tool \
  -et ./gallate.yaml \
  --engine.text-encoding=shift-jis

pfs-tool \
  -i ./gallate.yaml \
  --engine.rebuild-index
```

Rules:

- Engine option keys are arbitrary strings; the engine decides the
  schema.
- The `engine.` prefix is reserved for engine extensions.
- Standard CLI MUST NOT interpret any key under `--engine.*`. It
  passes them through verbatim.
- Standard CLI MUST expose engine options under a separate help
  section — see [02-cli-grammar.md § Help and version](./02-cli-grammar.md#help-and-version).

---

## 8.3 Engine media (audio / video / font / …)

The standard media set is just `text` and `image`. Everything else
is engine-extension. See [04-media.md](./04-media.md) for the full
classification.

When the engine exposes audio / video, they typically use:

```bash
--engine.audio.includes=voice
--engine.video.includes=cutscene
--engine.font.subset=true
```

The exact keys are engine-defined. Engines MAY also expose audio
/video as Shell-layer flags (`-a` / `-v`) — see
[04-media.md § Engine-extension media](./04-media.md#engine-extension-media).

---

## 8.4 Sub-media

Sub-media (`text.hardcoded`, `image.portrait_diff`, etc.) are
configured via `--engine.<media>.includes` and `--engine.<media>.excludes`.
Full syntax and semantics in
[04-media.md § Sub-Media](./04-media.md#sub-media).

The mechanism works identically for standard and extension media —
`--engine.audio.includes=voice` is valid for any engine that declares
`audio` and exposes `voice` as a sub-media.

---

## 8.5 Engine options in `gallate.yaml`

Engine options also live under `engine:` in YAML:

```yaml
engine:
  text_encoding: utf-8
  rebuild_index: true

  text:
    includes:
      - dialog
      - menu
      - hardcoded
    excludes:
      - debug_log

  audio:
    includes:
      - voice
    excludes:
      - bgm
```

Standard CLI ignores these. Engine wrapper reads them. Same precedence
rules apply (CLI > YAML > engine default).

---

## 8.6 Hard rules for engine extensions

1. **Do not modify standard parameter semantics.** `-e` stays
   `-e` (extract). `-t` stays `-t` (text). `--output` stays
   `--output`.
2. **Do not redefine standard parameters.** Don't invent `--output-dir`
   that conflicts with `--output` semantics.
3. **Use the engine namespace.** Every new flag has `--engine.`
   prefix.
4. **Document separately.** `tool --help` MUST list standard options
   first, then a separate "Engine Options" section.

Violating any of these is a contract breach. Wrappers rely on the
standard CLI surface staying stable.

---

## 8.7 Help output convention

```text
Standard Options:
   -e, -i                  operations
   -t, -i                  standard media
   --output, --ignore, --dry-run,
   --force, -v, -q

Engine Options (artemis):
   --engine.text-encoding=SHIFT-JIS|UTF-8|...
   --engine.rebuild-index[=true]
   --engine.text.includes=LIST
   --engine.image.excludes=LIST
```

The "Engine Options" section header MUST contain the engine id (from
[manifest](../protocol/03-discovery.md#manifest)) so users know which
engine the options apply to. A Wrapper can present this list
separately in its UI.