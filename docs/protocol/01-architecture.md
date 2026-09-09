# 01. Architecture

> Status: **Normative**. Defines the responsibility boundaries that
> every OmegaT / Wrapper / CLI implementation MUST respect.

---

## Three-layer model

```text
┌─────────────────────────────────────────┐
│                  OmegaT                 │
│       Translation / Review / XLIFF      │
└────────────────────┬────────────────────┘
                     │ Gamelate Wrapper API
                     │  (Wrapper is the only integration point)
                     ▼
┌─────────────────────────────────────────┐
│                 Wrapper                 │
│   GCWP client · project loader · glue   │
└────────────────────┬────────────────────┘
                     │ GCWP (YAML Line Protocol)
                     │  (CLI count is unbounded)
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   CLI #1         CLI #2         CLI #N
   Artemis         Ren'Py         Unity ...
       │             │             │
   Artemis        Ren'Py         Unity
   engine         engine         engine
```

The layers MUST NOT cross the responsibility boundaries below. In
particular, OmegaT MUST NOT integrate a CLI directly, and a CLI MUST NOT
require OmegaT-specific interfaces.

---

## OmegaT

Owns:

| Concern | Notes |
| --- | --- |
| XLIFF read & write | The canonical bilingual exchange format |
| Translation | Human translators; not specified by GCWP |
| Translation Memory (TM) | Per-project / shared |
| Terminology / Glossaries | Optional, engine-agnostic |
| Review & conflict resolution | Workflow UI |
| Filtering, search, editing | UI behavior |
| AI providers | Optional, generic |
| Validation UI | Visualizes results from the validator |
| Generic Validation Engine | Applies rules it received from the Wrapper |

OmegaT MUST NOT:

- Speak GCWP directly.
- Import engine-specific logic.
- Read or write game engine formats directly.

---

## Wrapper

Owns:

| Concern | Notes |
| --- | --- |
| CLI discovery | Finding available CLIs (filesystem, registry) |
| CLI process management | Spawn, monitor, terminate, clean up |
| Protocol translation | YAML Line Protocol ↔ OmegaT data structures |
| `gallate.yaml` loading | The project config file |
| Input / Output configuration | Translate to operation request |
| Event forwarding | Forward CLI events to OmegaT UI |
| Status aggregation | Snapshot + poll for status |
| Statistics aggregation | Collect / expose / pass to OmegaT |
| Validation rule import | Forward CLI rules to OmegaT Validator |
| Error normalization | Map CLI `error.code` to OmegaT dialogs |
| OmegaT integration | The single OmegaT integration surface |

Wrapper MUST NOT:

- Parse engine resources.
- Implement any extraction / injection algorithm.
- Modify images, audio, video, fonts.
- Understand engine-specific syntax.
- Implement its own translation workflow.

Wrapper MUST be:

- Engine-agnostic.
- Driven entirely by `manifest`, `features`, `validation`, and the event
  stream returned by the CLI.

---

## CLI

Owns:

| Concern | Notes |
| --- | --- |
| Game engine parsing | All engine-specific knowledge |
| `extract` | Read engine resources, write translation assets |
| `inject` | Read translated assets, write engine resources |
| `build` | Final packaged output (engine-specific) |
| `unpack` / `repack` | Engine archive management |
| Resource processing | Anything specific to the engine |
| Manifest / features / validation rules | Self-description |
| Event / status / statistics emission | Per GCWP |
| Exit code semantics | Per [02-core-protocol.md](./02-core-protocol.md) |

CLI MUST NOT:

- Display engine-specific GUI dialogs.
- Send messages such as `openArtemisDialog` / `showArtemisPanel`.
- Depend on OmegaT in any form.
- Require the Wrapper to understand engine internals.

---

## The single integration point

```text
OmegaT  ──┐
          │  ONE Wrapper instance per OmegaT process.
Wrapper ──┘  Adding CLIs requires no change to either side.
          │
          ├─ CLI #1
          ├─ CLI #2
          └─ CLI #N
```

The Wrapper is the **only** OmegaT integration point. Adding a 100th CLI
requires no change to OmegaT or the Wrapper — only a new CLI that speaks
GCWP. This is the architectural contract that prevents
the "adapter-per-engine" anti-pattern.

---

## Anti-patterns the architecture prevents

```text
Anti-pattern A — adapter-per-engine in OmegaT:

  OmegaT
   ├── ArtemisAdapter
   ├── RenPyAdapter
   ├── KiriKiriAdapter
   ├── UnityAdapter
   ├── ...
   └── unbounded

Anti-pattern B — CLI depending on OmegaT:

  CLI ←→ OmegaT API    ← CLI breaks when OmegaT changes
  CLI ←→ Wrapper API   ← CLI must rewrite per Wrapper
```

GCWP forbids both. See [12-compatibility.md](./12-compatibility.md) for
the rules that make this stable over time.