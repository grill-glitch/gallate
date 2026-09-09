# 07. Init

> Status: **Normative**. Defines the `init` subcommand for project
> initialization.

---

## 7.1 Purpose

`init` creates and initializes a standard gallate project. It is
**not** a resource-processing operation — it does not read or write
game data.

## 7.2 Basic form

```bash
tool init
```

Creates a project in the current directory. Equivalent to:

```bash
tool init ./
```

With a target path:

```bash
tool init ./projects/my-game
```

Creates `./projects/my-game/` and writes a `gallate.yaml` inside.

---

## 7.3 Options

| Flag | Purpose |
| --- | --- |
| `--input PATH` | Set the initial `input:` value |
| `--output PATH` | Set the initial `output:` value |
| `--ignore PATTERN` | Add an ignore pattern (repeatable) |
| `--media text,image` | Set the default `media:` list |
| `--force` | Overwrite an existing `gallate.yaml` |

---

## 7.4 Generated configuration

`init` writes `gallate.yaml` at the project root. The exact contents
depend on the flags given:

```bash
tool init ./projects/my-game \
  --input ./game.pfs \
  --output ./game-zh.pfs
```

Generates:

```yaml
input: ./game.pfs
output: ./game-zh.pfs
```

With ignore flags:

```bash
tool init ./projects/my-game \
  --input ./game.pfs \
  --output ./game-zh.pfs \
  --ignore "*.tmp" \
  --ignore "cache/"
```

Generates:

```yaml
input: ./game.pfs

ignore:
  - "*.tmp"
  - "cache/"

output: ./game-zh.pfs
```

With media flags:

```bash
tool init ./projects/my-game \
  --input ./game.pfs \
  --media text,image
```

Generates:

```yaml
input: ./game.pfs

media:
  - text
  - image
```

`--media` MAY be repeated; the final `media:` list is a deduplicated
union:

```bash
tool init ./projects/my-game \
  --media text,image \
  --media audio
```

Generates `media: [text, image]` (since `audio` is engine-extension
and `init` defaults to standard baseline only — see below).

---

## 7.5 Path resolution during init

All paths passed to `init` are resolved **against the final
project root**, not the shell's current directory.

```bash
tool init ./projects/my-game --input ./game.pfs
```

`./game.pfs` becomes `projects/my-game/game.pfs`, not
`<shell-cwd>/game.pfs`.

This makes a generated project portable — moving the project
directory does not introduce hidden path mismatches.

---

## 7.6 Default media in init

If `--media` is omitted, `init` writes the standard baseline only:

```yaml
media:
  - text
  - image
```

Engine-extension media (`audio`, `video`, `font`, etc.) are NEVER
written by `init` without an explicit flag. Engines that want audio
included by default should be opted in by the user via the project's
post-init configuration.

This rule prevents `init` from lying about a CLI's capabilities —
`text` and `image` are guaranteed by the spec; the rest depends on
the engine.

---

## 7.7 Force / overwrite protection

If the target directory already contains a `gallate.yaml`, `init`
MUST refuse to overwrite by default:

```text
Error: gallate.yaml already exists in ./projects/my-game.
Use --force to overwrite.
```

With `--force`, `init` overwrites the existing file. `--force` is
the standard escape hatch and applies to `init` only.

---

## 7.8 Project layout created by init

`init` MUST create the target directory and write `gallate.yaml`.
Whether `init` creates `text/` / `image/` directories is
engine-specific; standard CLI MAY create them as empty placeholders
but is not required.

Engine-extension directories (`audio/`, `video/`, `font/`, …) are
NEVER created by `init` — they appear only when the engine decides
to write into them, or when the user creates them by hand.

---

## 7.9 What `init` does NOT do

- It does NOT scan the input file (which may not exist yet).
- It does NOT pre-extract anything.
- It does NOT validate that the engine supports the declared
  `media:` — that's a runtime check on first `-e / -i`.

---

## 7.10 Examples

Create an empty project:

```bash
tool init ./projects/my-game
```

With input + output:

```bash
tool init ./projects/my-game \
  --input ./game.pfs \
  --output ./game-zh.pfs
```

With full defaults:

```bash
tool init ./projects/my-game \
  --input ./game.pfs \
  --output ./game-zh.pfs \
  --ignore "*.tmp" \
  --ignore "cache/" \
  --media text,image
```

Overwrite an existing project:

```bash
tool init ./projects/my-game --force
```