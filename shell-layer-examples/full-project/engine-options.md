# Engine options reference

This document lists every `--engine.*` option that this gallate CLI
accepts. It is **not** part of the gallate spec — each engine wrapper
defines its own. Use `tool --help` for the live list.

This file exists alongside `gallate.yaml` in the full-project example
so users can see both the YAML form and the corresponding
CLI override form.

---

## Plain options

| YAML key                | CLI flag                          | Purpose                              |
| ----------------------- | --------------------------------- | ------------------------------------ |
| `text_encoding`         | `--engine.text-encoding=utf-8`    | Encoding of source text              |
| `rebuild_index`         | `--engine.rebuild-index=true`     | Rebuild the resource index after inject |
| `compression`           | `--engine.compression=zstd`       | Compression for output archive       |

CLI override example:

```bash
tool -i ./gallate.yaml --engine.text-encoding=shift-jis
```

YAML override:

```yaml
engine:
  text_encoding: shift-jis
```

---

## Sub-Media options

| YAML key                             | CLI flag                                       | Purpose                       |
| ------------------------------------ | ---------------------------------------------- | ----------------------------- |
| `text.includes`                      | `--engine.text.includes=dialog,menu`           | Whitelist of text sub-media    |
| `text.excludes`                      | `--engine.text.excludes=debug_log`             | Subtractive list of text sub-media |
| `image.includes`                     | `--engine.image.includes=portrait`            | Whitelist of image sub-media   |
| `image.excludes`                     | `--engine.image.excludes=portrait_diff`        | Subtractive list of image sub-media |
| `audio.includes`                     | `--engine.audio.includes=voice,bgm`             | Whitelist of audio sub-media   |
| `audio.excludes`                     | `--engine.audio.excludes=sfx`                  | Subtractive list of audio sub-media |
| `video.includes`                     | `--engine.video.includes=cutscene`              | Whitelist of video sub-media   |
| `font.includes`                      | `--engine.font.includes=ascii,cjk`             | Whitelist of font sub-media    |

CLI override example:

```bash
tool -ei ./gallate.yaml \
  --engine.image.includes=portrait \
  --engine.image.excludes=portrait_diff
```

Equivalent YAML:

```yaml
engine:
  image:
    includes:
      - portrait
    excludes:
      - portrait_diff
```

---

## When CLI vs YAML?

- **CLI** for one-off invocations and quick experiments.
- **YAML** for project defaults you want every teammate to share.

CLI overrides YAML; CLI does NOT modify YAML.

---

## Discovering options

```bash
tool --help
```

Lists all standard options, then a separate "Engine Options" section
with engine-id in the header. The list above is what `tool --help`
prints for this engine.