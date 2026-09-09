# gallate

**Gallate** — A neutral specification set for CLI ↔ Wrapper communication in game localization workflows.

> ⚠️ This is the **specification repository**, not a runnable implementation.
> Implementations (Wrapper / CLI / OmegaT plugin) live in separate repositories.

---

## What is gallate?

`gallate` (formerly `gamelate`) defines two complementary contracts:

| Contract | Layer | Audience |
| --- | --- | --- |
| **GCWP** (Gamelate CLI–Wrapper Protocol) | Process / IPC layer | Wrapper & CLI implementers |
| **gallate.yaml** specification | Shell / project-config layer | CLI authors & end users |

The **GCWP** is the focus of this repository. It governs how a generic
**Wrapper** (the only OmegaT integration point) talks to many independent
**CLI** tools, each targeting one specific game engine, engine family, or
resource format.

```text
                OmegaT
                  │
                  │ Wrapper API
                  ▼
                Wrapper
                  │
                  │ GCWP
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    CLI #1     CLI #2     CLI #N
    Artemis    Ren'Py     Unity ...
```

> **OmegaT integrates only the Wrapper. CLI count is unbounded.**
> Adding a 100th engine requires no change to OmegaT or the Wrapper —
> only a new CLI that speaks GCWP.

The complementary **`gallate.yaml`** specification (CLI shell-level behavior
contract, project init, media model, script model, exit codes, …) is maintained
separately in
[`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents)
at the umbrella `Documents/` repository.

---

## Repository layout

```text
gallate/
├── README.md                  # this file (English)
├── README.zh-CN.md            # 中文版入口
├── LICENSE                     # CC BY-SA 4.0
├── CHANGELOG.md               # protocol version history
│
├── docs/protocol/
│   ├── README.md              # protocol index
│   ├── 00-glossary.md
│   ├── 01-architecture.md
│   ├── 02-core-protocol.md
│   ├── 03-discovery.md
│   ├── 04-operations.md
│   ├── 05-events.md
│   ├── 06-status.md
│   ├── 07-statistics.md
│   ├── 08-validation.md
│   ├── 09-diagnostics.md
│   ├── 10-configuration.md
│   ├── 11-process.md
│   ├── 12-compatibility.md
│   ├── 13-conformance.md
│   └── zh-CN/
│       ├── 00-glossary.md
│       ├── 01-architecture.md
│       ├── …
│       └── 13-conformance.md
│
├── schema/
│   ├── gcwp.schema.json
│   ├── manifest.schema.json
│   ├── features.schema.json
│   ├── request.schema.json
│   ├── response.schema.json
│   ├── event.schema.json
│   ├── status.schema.json
│   ├── statistics.schema.json
│   ├── validation.schema.json
│   └── cancel-command.schema.json
│
└── examples/
    ├── README.md
    ├── minimal-cli/
    │   ├── manifest.yaml
    │   ├── features.yaml
    │   └── extract.jsonl
    └── full-cli/
        ├── manifest.yaml
        ├── features.yaml
        ├── validation.yaml
        ├── extract.jsonl
        ├── inject.jsonl
        ├── build.jsonl
        └── errors.jsonl
```

---

## Relationship between layers

```text
Markdown   → explains  "why / how it is designed"
JSON Schema → enforces  "exactly what shape it must be"
Examples    → demonstrates "a complete working slice"
```

| Artifact | Author reads… | Author writes… |
| --- | --- | --- |
| Markdown spec | to understand intent | corrections via PR |
| JSON Schema | to know field requirements | type bindings / codegen |
| Examples | to see end-to-end behavior | copies as a starting template |

---

## Quick start: implement a Basic CLI

The minimum viable CLI that complies with GCWP must provide:

```text
manifest
features
one operation
exit codes
```

Concretely:

```bash
$ cli manifest --yaml
$ cli features --yaml
$ cli extract ./game.pfs --yaml
```

A worked minimal example lives at
[`examples/minimal-cli/`](./examples/minimal-cli/).

See [`docs/protocol/13-conformance.md`](./docs/protocol/13-conformance.md)
for the three conformance tiers (Basic / Standard / Full).

---

## Current protocol version

```text
name      : gcwp
version   : 1.0
status    : Draft
license   : CC BY-SA 4.0
```

See [`CHANGELOG.md`](./CHANGELOG.md).

---

## License

This specification is released under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

Reference implementations may choose any license, but the GCWP wire format
defined under `schema/` must remain stable per the compatibility rules in
[`docs/protocol/12-compatibility.md`](./docs/protocol/12-compatibility.md).

---

## Author

Samuel Flores
<5uniljdst@mozmail.com>

GitHub: [@grill-glitch](https://github.com/grill-glitch)