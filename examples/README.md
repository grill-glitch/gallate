# Examples

Worked reference implementations showing how a CLI speaks GCWP.

The files here are **trace recordings** of real CLI invocations
(re-typed by hand for clarity), not runnable binaries. They are meant
as templates CLI authors can copy.

---

## Layout

```text
examples/
├── README.md
├── minimal-cli/
│   ├── manifest.yaml             what the CLI says it is
│   ├── features.yaml             what the CLI claims it can do
│   └── extract.yaml-stream       a single extract operation end-to-end
└── full-cli/
    ├── manifest.yaml
    ├── features.yaml
    ├── validation.yaml           validation rules the CLI exposes
    ├── validation-result.yaml-stream  validation findings during an operation
    ├── extract.yaml-stream       full extract with progress + warnings
    ├── inject.yaml-stream        full inject with validation findings
    ├── build.yaml-stream         a complete build run
    ├── cancel.yaml-stream        cancellation mid-operation
    ├── identify.yaml-stream      Wrapper triages among candidate CLIs
    └── errors.yaml-stream        failure scenarios + error codes
```

The `.yaml-stream` extension is a convention to make streaming traces
obvious to humans; each line inside is YAML, **not** JSONL. CLI
implementations SHOULD emit YAML on stdout regardless of filename.
Use this extension to distinguish "streaming YAML" from "single YAML
documents" (`.yaml`) and "YAML Schema" definitions (`*.schema.yaml`).

If you see `.jsonl` anywhere in this repository it is a stale reference
and should be filed as a bug.

---

## minimal-cli — target tier: Basic

A minimum-viable CLI. Demonstrates:

```text
manifest
features
one operation (extract)
exit codes
```

See [`minimal-cli/`](./minimal-cli/).

---

## full-cli — target tier: Full

A complete CLI. Demonstrates:

```text
manifest (with targets) + features + validation
extract with progress + warnings + file events
inject with validation findings + statistics
build with phase events
identify across multiple candidate CLIs
failure modes with stable error codes
```

See [`full-cli/`](./full-cli/).

---

## Using them as a template

CLI authors SHOULD:

1. Copy `minimal-cli/` first.
2. Verify it satisfies Basic (handshake + one operation).
3. Add fields to features to claim Standard.
4. Add events to the operation stream.
5. Add `validation.yaml` content.
6. Add cancellation + status when claiming Full.
7. Add `manifest.targets` and a `cli identify` implementation when
   targeting a Wrapper (e.g. OmegaT plugin).

Wrapper authors SHOULD:

1. Read [`docs/protocol/03-discovery.md`](../../docs/protocol/03-discovery.md)
   first.
2. Use `manifest.targets` to pre-filter candidate CLIs per game
   path.
3. Use `minimal-cli/` traces to test the Basic path.
4. Use `full-cli/` traces to test cancellation, status, validation,
   and identify.

---

## Trace notation

```yaml
# Lines starting with `#` are comments — CLI implementations SHOULD
# NOT emit comment-prefixed lines on stdout.
#
# Empty lines are also for human readability only. CLI MUST emit
# one YAML document per non-empty, non-comment line on stdout.

{type: event, event: progress, current: 50, total: 100}
```