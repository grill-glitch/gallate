# 09. Standard Flags

> Status: **Normative**. Defines every standard long / short flag a
> gallate CLI must accept.

---

## 9.1 `--output PATH`

Override the output destination.

```bash
tool -i ./gallate.yaml --output ./game-zh.pfs
```

`--output` accepts either a file or a directory path:

```bash
tool -e ./gallate.yaml --output ./extracted/
```

The value is resolved relative to the Project Root unless absolute.
The CLI MUST NOT invent a new output path silently — if neither
`--output` nor YAML `output:` is given, the engine's default
behavior runs (typically in-place or error).

See [01-overview § Configuration Priority](./01-overview.md#15-configuration-priority).

---

## 9.2 `--ignore PATTERN`

Add a temporary ignore pattern. Repeatable.

```bash
tool -e ./gallate.yaml \
  --ignore "*.bak" \
  --ignore "cache2/"
```

Patterns use `.gitignore`-style glob:

```text
*        single-segment wildcard
**       multi-segment wildcard
?        single character
directory/   matches directories only
```

The CLI MUST support at least these. Engine-specific extensions are
allowed but not standardized.

### Merge semantics

CLI `--ignore` patterns **merge** with the YAML `ignore:` list
(they do NOT override).

```yaml
# gallate.yaml
ignore:
  - "*.tmp"
```

```bash
tool -e ./gallate.yaml --ignore "cache/"
```

Final ignore set: `["*.tmp", "cache/"]`.

### Scope

Ignore applies to the **entire resource lifecycle**:

```text
Resource Discovery
        ↓
Reading
        ↓
Extraction / Injection
        ↓
Writing
```

A resource matched by any ignore pattern is never read or written.

---

## 9.3 `--dry-run`

Plan the operation without executing it.

```bash
tool -i ./gallate.yaml --dry-run
```

Dry run MAY:

- Read `gallate.yaml`
- Resolve input, media, ignore
- Compute the planned output path
- Report what would have happened

Dry run MUST NOT:

- Modify game resources
- Write any output file
- Run pre/post scripts by default

The CLI SHOULD report a summary, for example:

```text
Operation : inject
Media     : text,image
Input     : ./game.pfs
Output    : ./game-zh.pfs
Ignored   : 13 resources
```

A Wrapper MAY interpret `--dry-run` to drive its own preview UI
based on the [GCWP statistics](../protocol/07-statistics.md) shape.

---

## 9.4 `--force`

Override safety checks. Currently only one use case:

```bash
tool init ./projects/my-game --force
```

Allows `init` to overwrite an existing `gallate.yaml`. Other
operations ignore `--force` (no safety check to override) unless an
engine defines one under its engine namespace.

---

## 9.5 `-v` / `--verbose`

Increase diagnostic detail on stderr. Repeatable:

```text
-v       default verbosity
-vv      most verbose (engine internals)
-vvv     reserved (engine extension if needed)
```

Log level MUST NOT change operation results. Higher verbosity shows
more diagnostic data on stderr; stdout (machine output) is unchanged.

---

## 9.6 `-q` / `--quiet`

Suppress non-essential output. For scriptable environments:

```bash
result=$(tool -e ./gallate.yaml -q)
```

The CLI MAY still emit warnings and errors on stderr, but not
progress bars or friendly banners.

The last flag wins: `-q -v` ⇒ verbose; `-v -q` ⇒ quiet.

---

## 9.7 `--engine.KEY=VALUE`

Engine extension option. See
[08-engine-extensions.md](./08-engine-extensions.md) for full
semantics. Examples:

```bash
--engine.text-encoding=utf-8
--engine.rebuild-index=true
--engine.text.includes=dialog,hardcoded
--engine.image.excludes=portrait_diff
```

---

## 9.8 `--help`

Show help and exit.

```text
Standard Options:
   -e, -i                  operations
   -t, -i                  standard media (engine extensions if exposed)
   --output PATH
   --ignore PATTERN
   --dry-run
   --force
   -v, -vv
   -q

Engine Options (artemis):
   (engine-specific)
```

The "Engine Options" section MUST include the engine id in its
header.

---

## 9.9 `--version`

Print the CLI version and exit.

```text
artemis-cli 1.2.0
protocol gcwp 1.0
engine artemis (2.x compatible)
```

The minimum required is the CLI version string. The full format is
engine-specific.

---

## 9.10 Summary table

| Flag                       | Short | Repeats | Standard? |
| -------------------------- | ----- | ------- | --------- |
| `--output`                 |       | no      | yes       |
| `--ignore`                 |       | yes     | yes       |
| `--dry-run`                |       | no      | yes       |
| `--force`                  |       | no      | yes       |
| `--verbose`                | `-v` | yes     | yes       |
| `--quiet`                  | `-q` | no      | yes       |
| `--engine.KEY=VALUE`       |       | yes     | yes (form) |
| `--help`                   | `-h` (recommended) | no | yes       |
| `--version`                |       | no      | yes       |

Flags not in this table are engine-extension and MUST NOT be added
without using the `--engine.*` namespace.