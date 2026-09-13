# 10. Configuration

> Status: **Normative**. Defines how the Wrapper translates the
> project-level `gallate.yaml` into a GCWP operation request.

---

## Two distinct layers

```text
gallate.yaml   →  PROJECT CONFIGURATION      (user-facing)
                  "what I want to do with this project"

GCWP request   →  RUNTIME COMMUNICATION      (Wrapper ↔ CLI)
                  "the resolved, machine-ready instruction"
```

The CLI never sees the raw `gallate.yaml`. The Wrapper does the
resolution and sends a flat request.

---

## Translation pipeline

```text
gallate.yaml
       ↓
    Wrapper
       ↓
    Request (over stdin)
       ↓
      CLI
```

Wrapper responsibilities:

1. Load `gallate.yaml`.
2. Resolve paths relative to Project Root.
3. Apply CLI `--engine.*` overrides.
4. Build a GCWP request.
5. Send it to the CLI.

CLI responsibilities:

1. Receive the request.
2. Execute.
3. Emit events / statistics.
4. Exit.

---

## gallate.yaml fields relevant to GCWP

The full `gallate.yaml` schema is defined in the companion specification
[`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents).
GCWP consumes only a subset:

| `gallate.yaml` field | GCWP request field |
| --- | --- |
| `input` | `request.input` |
| `output` | `request.output` |
| `ignore` | `request.ignore` |
| `scripts.pre / post` | handled by Wrapper, not GCWP |
| `engine.*` | flattened into `request.options` |
| `wrapper` | CLI selection (which executable to spawn) |

---

## Path resolution

All paths in the request are resolved **before** being sent:

```text
relative path   → resolved relative to gallate.yaml Project Root
absolute path   → used as-is
```

Example:

```yaml
# gallate.yaml
input: ./game.pfs
```

becomes

```json
{
  "input": [
    {
      "path": "./game.pfs",
      "kind": "file"
    }
  ]
}
```

The CLI is responsible for resolving the path itself, but using the same
convention. This avoids coupling CLI to a particular invocation directory.

---

## Wrapper as translator

```python
# Pseudocode for the Wrapper's translator

def translate(yaml_path, cli_overrides):
    project = load_gallate_yaml(yaml_path)
    project_root = dirname(yaml_path)

    request = {
        "type": "request",
        "id": generate_id(),
        "operation": project["operation"],  # from --operation flag
        "input": resolve_paths(project["input"], project_root),
        "output": resolve_paths(project["output"], project_root),
        "ignore": project.get("ignore", []),
        "options": merge_engine_options(project["engine"], cli_overrides),
    }

    return request
```

CLI implementations MUST NOT depend on this pseudocode; it is for
Wrapper authors only.

---

## Script handling

Pre/post scripts live in `gallate.yaml` and are **Wrapper** concern:

```yaml
scripts:
  pre:
    - ./scripts/unpack.py
  post:
    - ./scripts/repack.py
```

Wrapper runs them around the CLI operation. CLI never sees them.

---

## Project Root and CLI working directory

CLI working directory defaults to the gallate.yaml Project Root, not
the shell's current directory. This makes operations reproducible
across machines.

See [11-process.md § Working Directory](./11-process.md#working-directory).

---

## What the CLI does NOT receive

The CLI never receives:

- `gallate.yaml` itself
- Script definitions
- TM or glossary data
- Any OmegaT internal data

The CLI only receives the **resolved** GCWP request. This is what
makes the protocol engine-agnostic.