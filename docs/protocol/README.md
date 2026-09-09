# GCWP — Gamelate CLI–Wrapper Protocol

> ⚠️ **DRAFT — breaking changes possible.**
> Field names, schema shapes, and protocol behavior MAY change
> without notice until the 1.0 release. Pin to a commit hash, not
> a version, when depending on this specification.

This directory contains the formal specification of **GCWP**, the
process-level communication contract between a generic Wrapper and any
number of engine-specific CLI tools.

The companion **`gallate.yaml`** specification (Shell / project-config layer)
lives at
[`Documents/通用行为规范.txt`](https://github.com/grill-glitch/Documents).

---

## Document index

| # | Document | Scope |
| --- | --- | --- |
| 00 | [Glossary](./00-glossary.md) | Unified terminology |
| 01 | [Architecture](./01-architecture.md) | OmegaT / Wrapper / CLI responsibilities |
| 02 | [Core Protocol](./02-core-protocol.md) | Wire format, version, line protocol |
| 03 | [Discovery](./03-discovery.md) | manifest + features |
| 04 | [Operations](./04-operations.md) | extract / inject / build / unpack / repack |
| 05 | [Events](./05-events.md) | Real-time event stream |
| 06 | [Status](./06-status.md) | On-demand state snapshot |
| 07 | [Statistics](./07-statistics.md) | Result metrics |
| 08 | [Validation](./08-validation.md) | Engine-specific validation rules |
| 09 | [Diagnostics](./09-diagnostics.md) | stderr / error.code semantics |
| 10 | [Configuration](./10-configuration.md) | `gallate.yaml` ↔ GCWP request |
| 11 | [Process](./11-process.md) | Process lifecycle & cancellation |
| 12 | [Compatibility](./12-compatibility.md) | Versions, unknown fields |
| 13 | [Conformance](./13-conformance.md) | Basic / Standard / Full tiers |

Chinese translations: [`zh-CN/`](./zh-CN/)

Schemas: [`../schema/`](../schema/)

Examples: [`../examples/`](../examples/)

---

## Reading order

For a first read, follow this order:

```text
00-glossary → 01-architecture → 02-core-protocol
    ↓
03-discovery → 04-operations → 05-events
    ↓
06-status → 07-statistics
    ↓
08-validation → 09-diagnostics → 10-configuration
    ↓
11-process → 12-compatibility → 13-conformance
```

CLI authors who already know the architecture may skip directly to:

```text
03-discovery → 04-operations → 05-events
→ 08-validation → 13-conformance
```

Wrapper authors must read every chapter, with extra attention to:

```text
03-discovery → 05-events → 06-status → 07-statistics
→ 08-validation → 11-process → 12-compatibility
```

---

## Version

```text
name      : gcwp
version   : 1.0
status    : Draft
license   : CC BY-SA 4.0
```