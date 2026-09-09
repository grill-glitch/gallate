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
contract, project init, media model, script model, exit codes, …) is
documented in two places that together form one contract:

- This repository's [Shell-layer specification](./docs/shell-layer/)
  defines the project layout, CLI grammar, and the complete
  `gallate.yaml` schema.
- The historical reference
  [`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents)
  carries the prose narrative from which the Shell-layer spec was
  extracted.

---

## Repository layout

```text
gallate/
├── README.md                  # this file (English)
├── README.zh-CN.md            # 中文版入口
├── LICENSE                     # CC BY-SA 4.0
├── CHANGELOG.md               # placeholder (no entries during Draft)
│
├── docs/
│   ├── protocol/                # GCWP — Wrapper ↔ CLI process layer
│   │   ├── README.md              # protocol index
│   │   ├── 00-glossary.md
│   │   ├── 01-architecture.md
│   │   ├── …
│   │   ├── 13-conformance.md
│   │   └── zh-CN/                # Chinese translations
│   │
│   └── shell-layer/             # Shell / project-config layer
│       ├── README.md              # shell-layer index
│       ├── 00-glossary.md
│       ├── 01-overview.md
│       ├── 02-cli-grammar.md
│       ├── 03-operations.md
│       ├── 04-media.md
│       ├── 05-config-file.md
│       ├── 06-project-structure.md
│       ├── 07-init.md
│       ├── 08-engine-extensions.md
│       ├── 09-std-flags.md
│       ├── 10-stdout-stderr.md
│       ├── 11-conformance.md
│       └── zh-CN/                # Chinese translations
│
├── schema/                      # GCWP YAML Schemas (JSON Schema draft-07)
│   ├── gcwp.schema.yaml
│   ├── manifest.schema.yaml
│   ├── features.schema.yaml
│   ├── request.schema.yaml
│   ├── response.schema.yaml
│   ├── event.schema.yaml
│   ├── status.schema.yaml
│   ├── status-query.schema.yaml
│   ├── statistics.schema.yaml
│   ├── validation-rules.schema.yaml
│   ├── validation-result.schema.yaml
│   └── cancel-command.schema.yaml
│
├── examples/                    # GCWP IPC traces
│   ├── README.md
│   ├── minimal-cli/
│   │   ├── manifest.yaml
│   │   ├── features.yaml
│   │   └── extract.yaml-stream
│   └── full-cli/
│       ├── manifest.yaml
│       ├── features.yaml
│       ├── validation.yaml
│       ├── validation-result.yaml-stream
│       ├── extract.yaml-stream
│       ├── inject.yaml-stream
│       ├── build.yaml-stream
│       ├── cancel.yaml-stream
│       └── errors.yaml-stream
│
└── shell-layer-examples/        # Project-tree examples
    ├── README.md
    ├── minimal-project/
    │   ├── gallate.yaml
    │   ├── text/  image/
    └── full-project/
        ├── gallate.yaml
        ├── engine-options.md
        ├── text/  image/  audio/  video/  font/
        └── scripts/
            ├── unpack.py
            ├── repack.py
            └── .gitignore
```

---

## Relationship between layers

```text
Markdown        → explains   "why / how it is designed"
YAML Schemas    → enforces   "exactly what shape it must be"
Examples        → demonstrates "a complete working slice"
```

| Artifact | Author reads… | Author writes… |
| --- | --- | --- |
| Markdown spec | to understand intent | corrections via PR |
| YAML Schemas (JSON Schema semantics) | to know field requirements | type bindings / codegen |
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

## Current status

```text
name      : gallate (umbrella: GCWP + Shell layer)
status    : Draft — version is tracked per-protocol in CHANGELOG.md
license   : CC BY-SA 4.0
```

This repository is in active drafting. The protocol/wire-format
versions live in [`CHANGELOG.md`](./CHANGELOG.md); the documentation
itself has no version number and tracks the repository's git
history instead.

The Shell layer (project layout, CLI grammar, `gallate.yaml`) is a
separate document set under [`docs/shell-layer/`](./docs/shell-layer/).
Its contents evolve in lock-step with the Protocol layer.

---

## License

This specification is released under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

Reference implementations may choose any license, but the GCWP wire
format defined under `schema/` and the Shell-layer grammar defined
under `docs/shell-layer/` must remain stable per the compatibility
rules in [`docs/protocol/12-compatibility.md`](./docs/protocol/12-compatibility.md).

---

## Author

Samuel Flores
<5uniljdst@mozmail.com>

GitHub: [@grill-glitch](https://github.com/grill-glitch)