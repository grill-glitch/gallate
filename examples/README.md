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
│   ├── manifest.yaml      what the CLI says it is
│   ├── features.yaml      what the CLI claims it can do
│   └── extract.jsonl      a single extract operation end-to-end
└── full-cli/
    ├── manifest.yaml
    ├── features.yaml
    ├── validation.yaml    validation rules the CLI exposes
    ├── extract.jsonl      full extract with progress + warnings
    ├── inject.jsonl       full inject with validation findings
    ├── build.jsonl        a complete build run
    └── errors.jsonl       failure scenarios + error codes
```

`*.jsonl` is used here purely for trace legibility — each line is
YAML, not JSON. The `.jsonl` extension is a convention to make
streaming traces obvious to humans; CLI implementations SHOULD emit
YAML on stdout regardless of filename.

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
manifest + features + validation
extract with progress + warnings + file events
inject with validation findings + statistics
build with phase events
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

Wrapper authors SHOULD:

1. Read [`docs/protocol/03-discovery.md`](../../docs/protocol/03-discovery.md)
   first.
2. Use `minimal-cli/` traces to test the Basic path.
3. Use `full-cli/` traces to test cancellation, status, validation.

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