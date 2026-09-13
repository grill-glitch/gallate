# 12. Compatibility

> Status: **Normative**. Defines how CLI and Wrapper negotiate
> protocol versions and tolerate each other's additions.

---

## Protocol version

```text
MAJOR.MINOR
```

A CLI or Wrapper advertises the protocol version it speaks via
`manifest.protocol.version`. See
[02-core-protocol.md § Protocol version](./02-core-protocol.md#protocol-version).

---

## Bumping rules

### MAJOR

Incremented on **incompatible** changes:

- Renaming or removing fields.
- Changing the semantic meaning of an existing field.
- Changing the wire format (e.g. line protocol to something else).
- Repurposing a stable identifier (CLI id, error code, …).

Wrapper MAY refuse to start a CLI whose MAJOR it does not support.

### MINOR

Incremented on **backwards-compatible** additions:

- Adding new optional fields.
- Adding new values to an enum (in a way the existing values still work).
- Adding new event types.
- Adding new operations.

Old Wrapper MUST tolerate new fields; old Wrapper MAY ignore events it
does not understand.

---

## Unknown fields

Receivers MUST ignore unknown fields. Example:

```jsonl
{"type":"event","event":"progress","current":50,"total":100,"speed":123.4}
```

The pattern: **Unknown fields MUST be ignored.**

Exception: certain values are stable identifiers and may be rejected
when unknown:

```text
protocol major version    → may be rejected
event type                → ignored unless `type=command`
operation type            → rejected (unsupported operation, exit 4)
validation rule type      → ignored for unrecognized types
```

---

## Unknown events

```text
WRONG:
    if event == "unknown_event_type":
        raise ProtocolError

CORRECT:
    skip silently
```

Wrapper MUST ignore unknown event types. This lets CLIs evolve their
event vocabulary without breaking older Wrappers.

---

## Feature negotiation

When `features` reports a capability as `false`, Wrapper MUST NOT call
that capability. When a capability is omitted, Wrapper MUST treat it as
`false` (the "negative truth" rule from
[03-discovery.md § Negative truth](./03-discovery.md#negative-truth)).

Wrapper MAY re-query `features` between operations in case the CLI
has changed.

---

## Forward / backward compatibility matrix

| Change | Backward compatible? | Action |
| --- | --- | --- |
| Add optional field | yes | MINOR bump |
| Add new event type | yes | MINOR bump |
| Add new operation | yes | MINOR bump |
| Add new error code | yes | MINOR bump |
| Rename a field | **no** | MAJOR bump |
| Change field semantics | **no** | MAJOR bump |
| Repurpose error code | **no** | MAJOR bump |
| Remove optional field | **no** | MAJOR bump |
| Change line protocol | **no** | MAJOR bump |

---

## Stable identifiers

These fields MUST remain stable across compatible CLI updates:

```text
CLI id                      (manifest.id)
Engine id                   (manifest.engine.id)
Operation names             (request.operation values)
Feature names               (features.* keys)
Validation rule id          (rules[].id)
Validation rule type        (rules[].type: regex | placeholder | constraint)
Error code                  (event.code / response.code)
```

The **validation rule type** is itself a stable identifier. Adding new
rule types is a MINOR protocol bump; repurposing or removing an
existing value is a MAJOR protocol bump — see
[08-validation.md](./08-validation.md).

Wrapper MUST key off these values, never the human-readable strings.
See [12 § Error Code vs Message](./09-diagnostics.md#wrapper-rule).

---

## Identifiers that may change

```text
CLI human-readable name    (manifest.name)
CLI version string         (manifest.version)
Event message text         (event.message)
Validation rule message      (rules[].message)
Progress values
Statistics numbers
```

Wrapper MUST NOT depend on the byte content of these fields.

---

## CLI version vs Protocol version

The CLI's own version (in `manifest.version`) and the protocol version
(in `manifest.protocol.version`) are independent:

```text
manifest.version          CLI's release (e.g. 1.2.0)
manifest.protocol.version Protocol level (e.g. 1.0)
```

A CLI release may bundle any compatible protocol version.

---

## When to bump CLI vs Protocol

| CLI change | Bump |
| --- | --- |
| Fix a bug, internal refactor | CLI version (PATCH) |
| Add a feature flag (defaults to off) | CLI version (MINOR) |
| Add a new event type | CLI version (MINOR) + Protocol MINOR |
| Wire format change | Protocol MAJOR (and CLI MAJOR) |

---

## Final rule

> Adding the 100th CLI requires no Wrapper change.
> Adding the 100th Wrapper feature requires no CLI change.
> Adding a new GCWP feature is a MINOR bump — old sides ignore.