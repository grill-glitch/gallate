# 13. Project Metadata (`.meta.json`)

> Status: **Normative**. Defines the project-level state file
> `.meta.json` that the gallate CLI writes and maintains.

## 13.1 Design goals

`.meta.json` is the **Derived Project Metadata** for a gallate
project. It records the actual mapping between gallate project
files (under the Project Root) and the original game resources
from which they were extracted.

Rules:

- `.meta.json` is **auto-maintained by the CLI**. Users MUST NOT
  be required to create or edit it directly.
- `.meta.json` is **not** a user config file. It belongs to the
  CLI's bookkeeping.
- `.meta.json` lives in the **Project Root**, next to
  `gallate.yaml`.
- `.meta.json` MUST let subsequent `extract` / `inject` /
  `update` / `validate` operations find the source game file for
  each project file without re-scanning.
- The Wrapper MAY read `.meta.json` but MUST NOT infer, rebuild,
  or maintain the mapping on its own.

The core principle:

> `gallate.yaml` describes **how** the project should be
> processed. `.meta.json` describes **what** was actually
> established.

`.meta.json` is not a copy or mirror of `gallate.yaml`.

## 13.2 File location

```text
project/
├── gallate.yaml
├── .meta.json
└── ...
```

Standard location: the Project Root, next to `gallate.yaml`.

When `gallate.yaml` does not exist yet but a direct CLI operation
generates a mappable state, the CLI MAY still create `.meta.json`.
If `gallate.yaml` is later created or read, the CLI treats the two
files as different information layers — neither overwrites the
other.

## 13.3 Generation and modification rules

`.meta.json` MUST be written and modified by the gallate CLI based
on **actual execution results**.

Two trigger paths:

### 13.3.1 Direct CLI operation

```bash
gallate extract ./game ./project
```

The CLI processes the given input/output, observes the actual
result, and creates or updates `.meta.json` accordingly.

### 13.3.2 `gallate.yaml`-driven operation

```bash
gallate extract
```

The CLI reads `gallate.yaml`, executes the operation, and writes
`.meta.json` from the **observed** result — not by re-serializing
`gallate.yaml`:

```text
gallate.yaml
     │
     │ intent / configuration
     ▼
 CLI executes
     │
     │ observed result
     ▼
 .meta.json
```

`gallate.yaml` is intent. `.meta.json` is state.

## 13.4 Mapping model

`.meta.json` MUST be able to express the stable mapping between
gallate project files and original game resources.

Schema: [`schema/meta.schema.yaml`](../../schema/meta.schema.yaml).

Minimum example:

```json
{
  "schema_version": 1,
  "generated_by": {
    "id": "artemis",
    "version": "1.2.0"
  },
  "generated_at": "2026-09-09T12:34:56Z",
  "project": {
    "root": "."
  },
  "files": [
    {
      "project": "text/units/scenes_intro.json",
      "source": "scenes/intro.bin",
      "type": "text",
      "cli": {"id": "artemis", "version": "1.2.0"},
      "engine": {"id": "artemis", "version": "2.1"},
      "sub_media": "dialog"
    }
  ]
}
```

### 13.4.1 Standard fields

| Field | Required | Meaning |
| --- | --- | --- |
| `schema_version` | yes | Format version of this file. CLI refuses to load a `.meta.json` whose `schema_version` is higher than the CLI knows. |
| `generated_by` | yes | Which CLI wrote this file. Captures `manifest.id` and `manifest.version`. |
| `generated_at` | yes | ISO-8601 timestamp of last successful rewrite. |
| `project.root` | optional | Project Root path. |
| `files[]` | yes | Mapping entries, one per project file the CLI manages. |
| `files[].project` | yes | Path to the project file, **relative to the Project Root**. |
| `files[].source` | yes | Path to the original game resource. |
| `files[].type` | yes | Resource type. Standard media use the standard identifiers; engine-extension media use the namespace. |
| `files[].hash` | optional | Content hash of the project file. Algorithm-namespaced (e.g. `sha256:abc123…`). |
| `files[].size` | optional | Project file size in bytes at last write. |
| `files[].cli` | optional | CLI that last wrote this entry. |
| `files[].engine` | optional | Engine id + version this entry targets. |
| `files[].resource_id` | optional | Engine-internal logical id (e.g. entry name). |
| `files[].timestamp` | optional | ISO-8601 timestamp of this entry's last write. |
| `files[].encoding` | optional | Text encoding of the project file. |
| `files[].sub_media` | optional | Sub-Media identifier (`dialog`, `portrait_diff`, …). |
| `files[].extensions` | optional | Namespaced extension fields, one key per CLI. |

### 13.4.2 Extension fields

The CLI MAY add custom fields under `files[].extensions.<cli-id>`.
Extensions MUST NOT replace or override the meaning of any
standard field. Two CLIs MUST NOT both write to the same
extension namespace.

## 13.5 Mapping stability

The `project` / `source` relationship MUST be explicit.

The CLI:

- MUST NOT infer mappings from file names alone.
- MUST NOT infer source from directory names.
- MUST NOT require the Wrapper to re-derive the mapping.
- SHOULD prefer the existing `.meta.json` mapping when one
  exists.

For example, given:

```text
text/units/scenes_intro.json
```

the CLI MUST NOT treat this as a reliable hint for
`scenes/intro.bin`. The reliable source path lives in
`.meta.json` or comes from the current CLI operation that
established the mapping.

## 13.6 Lifecycle

```text
CLI command
  │
  ├── read gallate.yaml (if present)
  ├── parse input / output
  ├── execute the operation
  ├── determine which project files were created or modified
  └── create or update .meta.json
```

After a successful `extract`:

```text
project/
├── gallate.yaml
├── .meta.json
└── text/
    └── main.json
```

The next `inject` reads `.meta.json` and pairs:

```text
text/main.json
        │
        ▼
game/data/script.pfs
```

without re-scanning the game archive for source locations.

## 13.7 Update rules

When the CLI creates, modifies, moves, or deletes a project file
that already has a `.meta.json` entry, the CLI MUST update
`.meta.json` consistently.

### Create

A new project file gets a new entry.

### Modify

In-place edits that preserve the file's identity keep the
`project` / `source` mapping. The CLI updates `hash` and
`timestamp` (if present).

### Move

When a project file moves, the entry's `project` field updates:

```json
{
  "project": "new/path/main.json",
  "source": "game/data/script.pfs"
}
```

The `source` field is **not** lost. The CLI may keep the old entry
under a `_previous_project` field (engine-defined) for one
generation to support undo.

### Delete

When the CLI deletes a project file it owns, the corresponding
`.meta.json` entry is removed.

## 13.8 Consistency

The CLI MUST keep `.meta.json` consistent with the actual project
state. When the CLI detects drift:

```text
.meta.json ≠ actual project state
```

it MUST NOT silently produce a wrong mapping. The CLI may
report an error, report a warning, request regeneration, or
repair the mapping safely per the operation's semantics.

The CLI MUST NOT silently ignore:

- A `.meta.json` entry pointing at a project file that does not
  exist.
- A `.meta.json` entry pointing at a `source` resource that does
  not exist (engine resource missing).
- An ambiguous `project` / `source` mapping (one project file
  maps to multiple sources, or vice versa).
- An unrecognized `schema_version`.
- A `.meta.json` corrupted by an external program.

The specific recovery action is operation-defined; the rule is
**never silent corruption**.

## 13.9 Atomicity

`.meta.json` writes SHOULD be atomic.

Recommended pattern:

```text
generate temporary metadata
  ↓
validate
  ↓
atomic replace
  ↓
.meta.json
```

If the operation fails, the CLI MUST NOT commit a `.meta.json`
that describes a half-done state.

## 13.10 CLI ownership

`.meta.json` is a project-level public format, but each
`files[]` entry is owned by the CLI that wrote it.

Two CLIs sharing a project:

```text
CLI A ──┐
        ├── .meta.json
CLI B ──┘
```

MUST NOT silently overwrite each other's entries. The
`generated_by` field on each entry records ownership. CLIs MAY
edit only entries whose `cli.id` matches their own id, unless
the user explicitly tells them otherwise.

For shared project layouts, namespaces under
`files[].extensions.<cli-id>` provide room for cross-CLI
metadata without collisions.

## 13.11 Wrapper responsibilities

The Wrapper MAY read `.meta.json` to:

- Display project resources.
- Build resource management UI.
- Show the `project` / `source` mapping.
- Filter resources for the user.
- Coordinate CLI operations.

The Wrapper MUST NOT:

- Treat `.meta.json` as its own database.
- Rebuild the mapping from its own logic.
- Mutate CLI-managed entries.
- Duplicate the CLI's internal resource discovery logic.

The Wrapper is a **consumer and coordinator**, not a reimplementation.

```text
                 Gallate CLI
                     │
       ┌─────────────┴─────────────┐
       │                           │
       ▼                           ▼
 gallate.yaml                  实际操作
       │                           │
       └─────────────┬─────────────┘
                     ▼
                .meta.json
                     │
                     ▼
                  Wrapper
```

## 13.12 Relationship with `gallate.yaml`

| File             | Nature          | Source        | Role                                  |
| ---------------- | --------------- | ------------- | ------------------------------------- |
| `gallate.yaml`   | Intent / config | User or CLI   | Declares input, output, ignore, flow. |
| `.meta.json`     | Derived state    | CLI           | Records the actual file/resource mapping. |

```yaml
# gallate.yaml — intent
input: ./game
output: ./translation
ignore: ["*.tmp"]
```

```json
// .meta.json — state
{
  "files": [
    {"project": "translation/main.json", "source": "game/data/script.pfs", "type": "text"}
  ]
}
```

The two files are complementary, not interchangeable.

## 13.13 User visibility

`.meta.json` lives in the project but is not a user config.

- The CLI MUST NOT require the user to create it.
- The CLI MUST NOT require the user to maintain it via flags.
- The documentation MUST NOT tell normal users to edit it.
- If the user deletes `.meta.json`, the CLI MAY rebuild it from
  the next operation's actual results.
- If the user edits `.meta.json`, the CLI MAY treat it as an
  external modification and run consistency checks.

The presence of `.meta.json` SHOULD be transparent in normal
workflows.

## 13.14 Specification scope

`.meta.json` is part of the **Gallate Project Specification**, not
a private format of any single CLI.

- All compatible CLIs MUST follow the standard semantics of
  `.meta.json`.
- Engine CLIs MAY extend the format under
  `files[].extensions.<cli-id>`.
- Wrappers can consume the standard fields without knowing the
  specific engine implementation.
- The core semantics MUST stay decoupled from CLI internals.

```text
                Gallate Project
                      │
          ┌───────────┴───────────┐
          │                       │
   gallate.yaml              .meta.json
          │                       │
     用户意图                 实际状态
          │                       │
          └───────────┬───────────┘
                      │
                 Gallate CLI
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Engine A    Engine B    Engine C
          │           │           │
          └───────────┼───────────┘
                      ▼
                   Wrapper
```

This design preserves Unix philosophy: **the CLI performs the
work and produces explicit file state, the config describes
intent, the metadata records actual relationships, the Wrapper
composes, displays, and coordinates without duplicating the
CLI's internal logic.**