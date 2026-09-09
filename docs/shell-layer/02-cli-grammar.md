# 02. CLI Grammar

> Status: **Normative**. The exact command-line syntax a gallate CLI
> must accept.

---

## The grammar

```text
tool [operation][media] project [options]
```

Where:

```text
operation  = e | i                required (one of)
media      = (t|i|a|v)*          optional, any subset
project    = path to gallate.yaml required, positional
options    = zero or more flags   see 09-std-flags.md
```

`tool` is a placeholder; each CLI uses its own binary name
(`artemis-tool`, `pfs-tool`, etc.).

`project` MUST point at a `gallate.yaml`. The path is positional; CLI
MUST NOT look at the current directory to find it.

---

## Operation + Media shorthand

The operation flag is `-e` or `-i`; the standard media flags are
`-t` (text) and `-i` (image), appended directly. Media flags have
no separator:

```text
-et     = extract text
-ei     = extract image
-eti    = extract text + image
```

Engine-extension media (`-a` for audio, `-v` for video, etc.) are
appended the same way **when the engine has chosen to expose them**:

```text
-ea     = extract audio (engine-extension media, only present if exposed)
-ev     = extract video (engine-extension media, only present if exposed)
-etiav  = extract everything the engine supports (only valid for engines
          that expose audio + video)
```

The operation and media flags form a **single flag token** with no
separator. The order of media flags within the token is irrelevant
when they are all present. (When audio is an extension media, do
not mix its position with the standard `-t` and `-i` in ways that
change the meaning — order is still irrelevant for the set, but the
flag letters must be the ones the engine actually exposes.)

### Examples

```bash
tool -e ./gallate.yaml         # extract with project's default media
tool -et ./gallate.yaml        # extract text only
tool -etiav ./gallate.yaml     # extract everything (only engines exposing audio+video)

tool -i ./gallate.yaml         # inject with project's default media
tool -it ./gallate.yaml        # inject text only
tool -itai ./gallate.yaml      # inject text + audio + image
```

---

## Project target

The positional argument is a path to `gallate.yaml`:

```bash
tool -e ./gallate.yaml
tool -e ./projects/gamelate.yaml
tool -e /absolute/path/to/gallate.yaml
tool -e ../sibling-project/gallate.yaml
```

The CLI MUST refuse to run if the positional argument does not point
to a readable `gallate.yaml`. (Some CLIs MAY accept other extensions
like `gallate.yml`; this is engine-specific and not standardized.)

---

## Standard options

Beyond the operation/media shorthand, a gallate CLI accepts the
following standard long flags:

```text
--output PATH       Override output destination (file or directory)
--ignore PATTERN    Add a temporary ignore pattern (repeatable)
--dry-run           Plan without executing
--force             Override safety checks (currently: init overwrite)
-v / --verbose      Increase diagnostics (repeatable: -vv)
-vv                 Most verbose
-q / --quiet        Reduce non-essential output
--engine.KEY=VALUE  Engine extension option
```

The media short flags (`-t`, `-i`, and any extension `-a` / `-v` the
engine exposes) are part of the operation flag, not separate
options. Full semantics in [09-std-flags.md](./09-std-flags.md).

---

## Help and version

Standard:

```bash
tool --help
tool --version
```

`--version` SHOULD print the CLI version (from `manifest.version`,
see [Protocol § Manifest](../protocol/03-discovery.md#manifest)),
the protocol version it speaks, and the engine id it wraps. The
exact format is engine-specific; the *minimum* required is the CLI
version string.

`--help` SHOULD group options under two headings:

```text
Standard Options:
  -e, -i                  operations
  -t, -i, -a, -v          media
  --output, --ignore,
  --dry-run, -v, -q,
  --force
  --engine.KEY=VALUE

Engine Options:
  (engine-specific options listed here)
```

Engine options MUST be under a separate heading so users can see
what is standard and what is engine-specific.

---

## What a gallate CLI MUST accept

The following invocations MUST all be parseable:

```bash
tool -e ./gallate.yaml
tool -e ./gallate.yaml --output ./out/
tool -et ./gallate.yaml --ignore "*.tmp" --ignore "cache/"
tool -i ./gallate.yaml --dry-run
tool -etiav ./gallate.yaml -vv -q   # equivalent to -vv; -q wins per last-wins rule
```

A CLI MAY accept additional non-standard long flags, but MUST NOT
reuse standard flag names with different semantics.