# 13. Conformance

> Status: **Normative**. Defines three conformance tiers a CLI can
> claim. This lets implementers pick a target level and lets Wrapper
> authors decide which CLIs they can drive.

A CLI MUST declare its tier via the `features` document.

---

## Tier summary

```text
Basic      manifest + features + one operation + exit codes
           → can answer "what are you, what can you do, run one job"

Standard   Basic + events + statistics + validation
           → can drive a real OmegaT workflow

Full       Standard + cancellation + status streaming + diagnostics
           → can drive an interactive, cancellable Wrapper UI
```

---

## Basic

### Required

- Manifest
- Features
- At least one operation (`extract`, `inject`, `build`, `unpack`,
  `repack`, or an engine-extension name)
- Standard exit codes
- Operation Request parsing
- Stdout/stderr separation (no free-form text on stdout)

### Features that MUST be true

```yaml
operations:
  extract: true   # or any one standard/engine-extension operation
```

### Optional at this tier

- Events other than `started` and `completed`
- Statistics
- Validation rules
- Cancellation
- Status query

### Worked example

[`examples/minimal-cli/`](../../examples/minimal-cli/) implements Basic.

```bash
$ minimal-cli manifest --yaml
$ minimal-cli features --yaml
$ minimal-cli extract ./game.pfs --yaml
```

---

## Standard

### Required

- Everything in Basic
- Event streaming for at least: `started`, `progress`, `file`, `completed`
- Statistics emission (in the `completed` event or as a separate
  `statistics` event)
- Validation rules via `cli validation --yaml` for at least one of
  `regex` / `placeholder` / `constraint`

### Features that MUST be true

```yaml
runtime:
  events: true
  statistics: true
validation:
  regex: true       # at least one of regex / placeholder / constraint
```

### Optional at this tier

- Cancellation
- Status query
- All validation types

### Wrapper assumption

A Wrapper that supports Standard MUST be able to drive any Standard
CLI without inspecting its `id`.

---

## Full

### Required

- Everything in Standard
- Cancellation via `cancel` command
- Status query via `cli status --yaml`
- All validation rule types
- Standard error codes (or engine equivalents documented)
- Diagnostic stream on stderr (human-readable progress, warnings)

### Features that MUST be true

```yaml
runtime:
  events: true
  status: true
  statistics: true
  cancellation: true
validation:
  regex: true
  placeholder: true
  constraint: true
```

### Wrapper assumption

A Wrapper that supports Full MUST be able to drive any Full CLI,
including interactive cancellation and live status polling.

---

## How tiers compose

| Tier | Wrapper requirement | CLI requirement |
| --- | --- | --- |
| Basic | can launch one CLI, read exit code | implement Basic |
| Standard | can drive OmegaT loop with progress | implement Standard |
| Full | can drive interactive UI with cancel | implement Full |

A Wrapper that supports tier X MUST also drive all CLIs at tier Y where
Y < X (it just won't use the extras).

---

## Picking a tier

```text
Bare extraction script → Basic
Production CLI for an engine → Standard
CLI for an interactive Wrapper → Full
```

A CLI SHOULD aim for Standard at minimum unless the use case is
strictly scripted.

---

## Conformance claim

CLI documentation MUST declare its tier:

```text
This CLI conforms to GCWP 1.0 (Standard).
```

The claim SHOULD match the truth in the `features` document.

---

## Test suite

A reference test harness (planned) will exercise:

```text
Basic    handshake + one operation + exit code matrix
Standard events stream + statistics + one validation rule type
Full     cancellation + status streaming
```

Until the harness ships, authors SHOULD self-test against the worked
examples:

```text
examples/minimal-cli/      ← target Basic
examples/full-cli/         ← target Full
```