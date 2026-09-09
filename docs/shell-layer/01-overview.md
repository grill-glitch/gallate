# 01. Overview

> Status: **Normative**. Defines the three design principles the
> Shell layer rests on.

---

## 1.1 Unix Philosophy

The gallate CLI focuses on resource handling:

```text
extract    (-e)
inject     (-i)
```

The CLI is **not** responsible for:

- Translation
- Review
- Terminology management
- Translation memory
- AI translation

Those functions live in separate tools or processors (OmegaT, MT
pipelines, terminology databases, …). The gallate CLI is the bridge
between the engine and those tools.

---

## 1.2 Engine Specific

One CLI targets **one** specific engine, engine family, or resource
format:

```text
artemis-tool
pfs-tool
renpy-tool
unity-tool
```

Different CLIs may have wildly different implementations but MUST obey
the same Shell-layer behavior contract.

This complements the
[Protocol-layer principle](../protocol/01-architecture.md#engine-cli)
— at the Shell layer the rule is "one CLI per engine"; at the
Protocol layer the rule is "Wrapper speaks to any of them via GCWP".

---

## 1.3 Project-Centric

The standard Project Target is `gallate.yaml`. The CLI does not accept
the game file or game directory directly.

### Legal

```bash
tool -e ./gallate.yaml
```

### Not legal

```bash
tool -e ./game.pfs
tool -e ./www/
```

Game files, directories, and resource locations are all described by
`gallate.yaml`.

This gives a stable layer where:

```text
CLI Interface
    ↓
stable

Project Configuration
    ↓
changeable
```

The project's internal layout can change; the CLI invocation never has
to.

---

## 1.4 Configuration vs Operation

`gallate.yaml` describes:

> The **default** behavior for this project.

CLI flags describe:

> The **override** for this invocation.

CLI overrides the project config but does not modify it by default.
See [01-overview § Configuration Priority](#15-configuration-priority).

---

## 1.5 Configuration Priority

```text
CLI
 ↓
gallate.yaml
 ↓
Engine Default
```

CLI explicit args win over YAML; YAML wins over engine default.

**Different config items have different override semantics.** Do not
treat them uniformly:

```text
Media       CLI → fully overrides YAML
Ignore      CLI → MERGES with YAML
Output      CLI → overrides YAML
Scripts     CLI → cannot override YAML (pre/post are YAML-only)
```

See individual chapters:

- Media: [04-media.md](./04-media.md)
- Ignore: [09-std-flags.md § Ignore](./09-std-flags.md#ignore)
- Output: [09-std-flags.md § Output](./09-std-flags.md#output)
- Scripts: [05-config-file.md § scripts](./05-config-file.md#scripts)

---

## 1.6 What this spec is and is not

This spec defines:

> The **CLI behavior contract** — what a gallate CLI does when invoked
> from a shell.

This spec does NOT define:

> The **internal implementation** of any specific game engine.

That is the engine wrapper's job.