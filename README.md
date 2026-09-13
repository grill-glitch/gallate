# gallate

<p align="center">
  <img src="./docs/assets/gallate-logo.png" alt="gallate logo" width="640">
</p>

**[English](./README.md) | [简体中文](./README.zh-CN.md)**

**Gallate** — A neutral specification set for CLI ↔ Wrapper communication in game localization workflows.

> ⚠️ **DRAFT — breaking changes possible.**
> The specification is in active drafting. Field names, schema
> shapes, and protocol behavior MAY change without notice until the
> 1.0 release. Pin to a commit hash, not a version, when depending
> on this repository.

---

## Philosophy

> **One generic Wrapper bridges OmegaT to countless independent CLIs;
> standardize the protocol, not the implementation.**

`gallate` is not "yet another translation tool." It is the
**protocol layer** that lets a single OmegaT integration talk to
any number of independent engine-specific CLIs — without OmegaT,
the Wrapper, or the CLIs ever needing to know about each other.

```text
                OmegaT
                  │
                  │  (one Wrapper API)
                  ▼
                Wrapper
                  │
                  │  GCWP
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    CLI #1     CLI #2     CLI #N
    Artemis    Ren'Py     Unity ...
       │          │          │
    Engine     Engine     Engine
```

### Why this matters

1. **Highly decoupled.** OmegaT, the Wrapper, every CLI, and every
   game engine evolve independently. Replacing one layer never
   requires rewriting the others.
2. **Real Unix philosophy.** Each CLI is a focused, independent tool.
   It can run alone, from a shell, from a CI pipeline, from a GUI,
   or from OmegaT — same binary, same flags.
3. **Unbounded extensibility.** One Wrapper, *N* CLIs, with no upper
   limit:

   ```text
   Wrapper
   ├── CLI A
   ├── CLI B
   ├── CLI C
   └── ...
   ```

   Adding a 100th engine requires no Wrapper changes — only a new
   CLI that speaks GCWP.
4. **Protocol over language.** A CLI does not have to be Rust, Go,
   or Python. As long as it follows GCWP, it joins the ecosystem.
5. **Deployment handled by the Wrapper.** The Wrapper discovers,
   downloads, validates, and updates CLIs. Users never wrestle with
   per-engine runtimes.
6. **OmegaT is one consumer.** Wrapper does not bind translation
   logic to OmegaT; CLIs do not depend on OmegaT. Any future GUI,
   CLI, or automation pipeline can drive the same CLIs.
7. **Ecosystems evolve independently.** CLIs ship on their own
   cadence, the Wrapper ships on its own, OmegaT ships on its own —
   no co-release pressure.
8. **Capability discovery is the contract.** `manifest`, `features`,
   `status`, `statistics` — the Wrapper asks the CLI what it can do
   rather than assuming.

The result is a system where the **core is a small, stable protocol**
that lets many specialized tools compose freely — not a "big, beautiful
translation software" that everyone has to fork.

---

## What is gallate?

`gallate` (formerly `gamelate`) defines two complementary contracts:

| Contract | Layer | Audience |
| --- | --- | --- |
| **GCWP** (Gamelate CLI–Wrapper Protocol) | Process / IPC layer | Wrapper & CLI implementers |
| **`gallate.yaml`** specification | Shell / project-config layer | CLI authors & end users |
| **`.meta.json`** (Derived Project Metadata) | Project state | CLIs (writer), Wrappers (reader) |

`gallate.yaml` is **intent** — what the project should do. `.meta.json`
is **state** — what the project actually did. The two are
complementary, not interchangeable. See
[docs/shell-layer/13-meta-json.md](./docs/shell-layer/13-meta-json.md).

The **GCWP** sits under [`docs/protocol/`](./docs/protocol/). The
**Shell-layer specification** sits under
[`docs/shell-layer/`](./docs/shell-layer/) and covers the CLI grammar,
project layout, and the `gallate.yaml` schema. Together they cover
everything OmegaT / the Wrapper / / any CLI implementation needs.

> **The Wrapper is the only OmegaT integration point. CLI count is
> unbounded.** Adding a 100th engine requires no change to OmegaT or
> the Wrapper — only a new CLI that speaks GCWP.

The historical narrative reference for the Shell-layer rules lives
at [`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents);
it is the prose from which the Shell-layer spec was extracted.

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
│   ├── assets/
│   │   └── gallate-logo.png    # project logo (README hero)
│   │
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
│   ├── identify.schema.yaml
│   └── cancel-command.schema.yaml
│
├── examples/                    # GCWP IPC traces
│   ├── README.md
│   ├── minimal-cli/
│   │   ├── manifest.json
│   │   ├── features.json
│   │   └── extract.jsonl
│   └── full-cli/
│       ├── manifest.json
│       ├── features.json
│       ├── validation.json
│       ├── validation-result.jsonl
│       ├── extract.jsonl
│       ├── inject.jsonl
│       ├── build.jsonl
│       ├── cancel.jsonl
│       ├── identify.jsonl
│       └── errors.jsonl
│
└── shell-layer-examples/        # Project-tree examples
    ├── README.md
    ├── minimal-project/
    │   ├── gallate.yaml
    │   ├── .meta.json
    │   ├── text/  image/
    └── full-project/
        ├── gallate.yaml
        ├── .meta.json
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
$ cli manifest
$ cli features
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

## Reference implementations

A CLI that conforms to this specification exists as a standalone
repository. It's not part of the spec itself — implementations live
on their own cadence and ship independently.

| Engine   | CLI id       | Conformance       | Repository                                                                 |
| -------- | ------------ | ----------------- | --------------------------------------------------------------------------- |
| Ren'Py 7 | `sirenhead`  | GCWP 1.0 Standard  | [`grill-glitch/gallate-renpy`](https://github.com/grill-glitch/gallate-renpy) |

The Ren'Py CLI ships both layers of the spec:

- **Shell layer** — `tool -et ./gallate.yaml` to extract, `-it` to
  inject. Standard flags (`--output`, `--ignore`, `--dry-run`,
  `--engine.KEY=VALUE`).
- **Protocol layer (GCWP)** — same binary driven via JSON Lines on
  stdin/stdout. Implements `manifest`, `features`, `validation`,
  `identify`, `extract`, `inject` operations, event streaming,
  statistics, and validation rules.

Notable behaviors verified end-to-end on a real Ren'Py game:

- Byte-identical round-trip on text and image/audio/video assets.
- Source-drift detection (exit 8, atomicity preserved).
- Minimal-diff text inject (N edits → exactly N changed lines).
- Sub-media classification (`image` → `background` / `portrait` /
  `cg` / `ui`; `audio` → `voice` / `bgm` / `sfx`; `video` →
  `cutscene` / `opening` / `ending`) driven by `script.rpy` ref
  scan + filename hints + folder conventions, overridable via
  `gallate.yaml`'s `engine.<media>.{includes,excludes}`.

This list is **not exhaustive** — the Wrapper discovers CLIs via
`manifest.targets` and the GCWP handshake, so any engine CLI that
speaks the protocol joins the ecosystem automatically.

---

## Author

Samuel Flores
<5uniljdst@mozmail.com>

GitHub: [@grill-glitch](https://github.com/grill-glitch)