# 08. Validation

> Status: **Normative**. Defines how a CLI exposes engine-specific
> text validation rules to the Wrapper, which forwards them to OmegaT's
> generic validation engine.

Validation is the most valuable capability GCWP exposes to OmegaT: it
is the only path by which engine knowledge reaches the translator's UI.

---

## Validation flow

```text
CLI
  ↓
Engine Validation Rules       (declarative)
  ↓
Wrapper
  ↓
OmegaT Validation Engine      (generic, applies rules)
  ↓
XLIFF                         (findings attached per translation unit)
```

The CLI MUST NOT build its own review GUI. The Wrapper MUST NOT
re-implement engine-specific validation. The OmegaT validator MUST NOT
hardcode engine knowledge.

---

## Validation rules document

Schema: [`schema/validation.schema.yaml`](../schema/validation.schema.yaml).

Interface:

```bash
cli validation --yaml
```

Example:

```yaml
type: validation

rules:
  - id: control-code
    type: regex
    scope: text
    pattern: "\\[A-Z]+(?:_[0-9]+)?"
    flags: []
    severity: error

  - id: player-name
    type: placeholder
    scope: text
    pattern: "\\{player\\}"
    preserve: true
    severity: error

  - id: max-length
    type: constraint
    scope: text
    constraint:
      maxLength: 80
    severity: warning
```

---

## Rule fields

| Field | Required | Notes |
| --- | --- | --- |
| `id` | ✓ | Stable rule identifier. |
| `type` | ✓ | One of `regex`, `placeholder`, `constraint`. |
| `scope` | ✓ | Where the rule applies. |
| `severity` | ✓ | `info`, `warning`, `error`. |
| `message` | optional | Override for the result message. |
| `description` | optional | Human-readable explanation. |

---

## Regex Rule

The most basic engine-specific check.

```yaml
id: control-code
type: regex
scope: text
pattern: "\\[A-Z]+(?:_[0-9]+)?"
flags: []
severity: error
```

Pattern is a regular expression (engine-defined flavor — Wrapper SHOULD
default to PCRE/RE2 if no engine hint).

---

## Placeholder Rule

Use this instead of regex for placeholders.

```yaml
id: player-name
type: placeholder
scope: text
pattern: "\\{player\\}"
preserve: true
severity: error
```

Semantics:

```text
Source:
    Hello {player}

Target:
    你好 {player}      ✓ pass

Target:
    你好               ✗ fail: required placeholder missing
```

`preserve: true` means the placeholder MUST appear unchanged in target.

---

## Constraint Rule

Rules that don't fit regex:

```yaml
id: max-length
type: constraint
scope: text
constraint:
  maxLength: 80
severity: warning
```

Standard constraint fields:

| Constraint | Meaning |
| --- | --- |
| `maxLength` | Max characters in target text. |
| `minLength` | Min characters. |
| `maxBytes` | Max bytes after UTF-8 encoding. |
| `noLineBreak` | Target MUST NOT contain line breaks. |

---

## Scope

```text
text        any text
source      source text only
target      translated text only
placeholder placeholder region
metadata    metadata fields
resource    whole resource
```

Example:

```yaml
scope: target
```

means the rule applies only to the translation, not the source.

---

## Severity

| Severity | Meaning |
| --- | --- |
| `info` | Informational; doesn't block workflow. |
| `warning` | Warning; workflow continues. |
| `error` | Error; blocks final commit/build by default. |

OmegaT MAY let users change the visual representation but MUST NOT
change the rule definition returned by the CLI.

---

## Validation Result

When the CLI evaluates a rule against a translated unit, it emits:

```yaml
type: validation
rule: placeholder
severity: error

source: Hello {player}
target: 你好

message: Required placeholder is missing: {player}

file: script/scene_037.bin
line: 42
offset: 12
length: 8
```

Optional context fields:

```text
file
line
offset
length
resource
translation_unit
```

---

## Layered rules

Three rule sources combine:

```text
Engine    from cli validation --yaml
Project   from gallate.yaml  (per-project rule overrides/additions)
User      from OmegaT user preferences (last-line, highest priority)
```

Effective rule set:

```text
Effective = Engine + Project + User
```

Priority:

```text
User > Project > Engine
```

CLI MUST NOT ship rules that override user rules. CLI MAY provide
sane defaults, but the final composition is the Wrapper's job.

---

## Validator placement

CLI MUST NOT validate in its own UI.

```text
WRONG:
    CLI runs regex → emits dialog "control code missing"

CORRECT:
    CLI emits rule description
    Wrapper registers rule in OmegaT Validator
    OmegaT shows finding in its standard UI
```