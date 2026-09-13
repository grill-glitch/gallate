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
│   ├── manifest.json             what the CLI says it is
│   ├── features.json             what the CLI claims it can do
│   └── extract.jsonl             a single extract operation end-to-end
└── full-cli/
    ├── manifest.json
    ├── features.json
    ├── validation.json           validation rules the CLI exposes
    ├── validation-result.jsonl   validation findings during an operation
    ├── extract.jsonl             full extract with progress + warnings
    ├── inject.jsonl              full inject with validation findings
    ├── build.jsonl               a complete build run
    ├── cancel.jsonl              cancellation mid-operation
    ├── identify.jsonl            Wrapper triages among candidate CLIs
    └── errors.jsonl              failure scenarios + error codes
```

The `.jsonl` extension marks streaming protocol traces: each
line is a single JSON object — the standard [JSON Lines][jsonl]
(NDJSON) format. CLI implementations emit one JSON value per line on
stdout. Use this extension to distinguish streaming JSONL from
single-object discovery responses (`.json`).

Discovery commands (`cli manifest`, `cli features`,
`cli validation`, `cli identify <path>`, `cli status`) emit a
single JSON object on stdout and use the `.json` extension.
Streaming operations (`extract`, `inject`, `build`, `cancel`,
`events`, `status-query`) use `.jsonl`.

The `gallate.yaml` project file stays YAML — it is the **only** YAML
in this repository. The JSON Schema files in `schema/*.schema.yaml`
are stored in YAML syntax (GCWP convention) but their semantics
are JSON Schema draft-07; they are not the same as user-facing
YAML.

[jsonl]: https://jsonlines.org/

If you see a `.yaml` file in `examples/` it is a stale reference
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
5. Add `validation.json` content.
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

```jsonl
# Lines starting with `#` are comments — CLI implementations SHOULD
# NOT emit comment-prefixed lines on stdout.
#
# Empty lines are also for human readability only. CLI MUST emit
# one JSON document per non-empty, non-comment line on stdout.

{"type":"event","event":"progress","current":50,"total":100}
```
