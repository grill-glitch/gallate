# Changelog

> ⚠️ **DRAFT — breaking changes possible.**
> The gallate specification is in active drafting. Field names,
> schema shapes, and protocol behavior MAY change without notice
> until the 1.0 release. Pin to a commit hash, not a version,
> when depending on this specification.

The gallate specification is in active drafting. While the
specification is Draft, the repository has **no published version
number** — there are no entries here.

What changes during drafting:

- Documentation rewrites
- New schema additions
- New examples
- Renames / reorganizations

None of these are versioned. The repository's git history is the
authoritative record of changes during drafting.

When the specification reaches 1.0, entries will follow
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format,
and the protocol version will follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) at the
protocol/wire-format layer only — not the documentation layer.

Until then, this file stays empty.

---

## Draft-stage renames (not yet a numbered release)

These changes happened during Draft before any versioned release.
They are recorded here for traceability; CLI implementers and
Wrapper authors SHOULD pin to a commit hash that includes them.

### `features.resources` → `features.media` (Draft rename)

The top-level capability key returned by `cli features --yaml`
was previously called `resources`. It is now `media` to eliminate
ambiguity with the per-resource notion used elsewhere
(`resource path`, `resource id`, `per-resource tree`).

- The field semantics are unchanged: a map of media identifier to
    support flag.
- The CLI behaviour that distinguishes baseline media (`text`,
    `image`) from engine-extension media (`audio`, `video`, …) is
    unchanged.
- `event: resource`, `validation-result.resource`, and
    `status.current.resource` are per-resource fields and are
    unaffected.

Affected files:

- `schema/features.schema.yaml` — top-level key renamed.
- `examples/{minimal-cli,full-cli}/features.yaml` — examples updated.
- `docs/protocol/03-discovery.md` and its Chinese translation —
    table column and prose updated.
- `docs/shell-layer/04-media.md` and its Chinese translation —
    YAML example updated.

### Per-media configuration blocks in `gallate.yaml`

New top-level keys added to `gallate.yaml`:

- `text` — configures text-media output (XLIFF / PO / JSON),
  layout (`flat` / `mirror` / `single`), per-translation-unit
  metadata (`original_file`, `source_context`, `location`,
  `engine_path`), and source-context capture for `text.hardcoded`
  strings (`context_lines`, `max_bytes`, `engine_extensions`).
- `image` / `audio` / `video` — layout, manifest, sidecar hints.
- Engine-extension media follow the same shape.

The `original-file` field gives every translation unit the source
path inside the game archive. The `source-context` field gives
`text.hardcoded` units the surrounding lines of code so a
translator can read the actual usage. Both are configurable; the
defaults are sensible.

This is a project-config change only — no CLI protocol change.
Wrapper / OmegaT implementations that already ignore unknown
top-level keys will work unchanged.

Affected files:

- `docs/shell-layer/05-config-file.md` and its Chinese translation —
    top-level field table, complete example, new `§5.8 Per-media
    output configuration` chapter with `text` / `image` / `audio`
    / `video` blocks and XLIFF / PO / JSON examples.
- `docs/shell-layer/12-file-structure.md` (new chapter) and its
    Chinese translation — covers `text/units/` layout modes,
    naming convention, `manifest.yaml`, per-format details, and
    sub-media directories under `image/` / `audio/` / `video/`.
- `docs/shell-layer/README.md` and its Chinese translation —
    index updated to include chapter 12.
- `docs/shell-layer/examples/full-project/gallate.yaml` and
    `docs/shell-layer/examples/minimal-project/gallate.yaml` —
    reference examples updated with the new `text:` block.

### Source-context: normative four-field data model

The `text.hardcoded` source-context previously documented three
"representations" (XLIFF / PO / JSON), with no canonical model.
This was a divergence hazard — different CLIs produced
incompatible files.

Replaced with a single **four-field data model** (`file` /
`line` / `end_line` / `snippet`) that is the same regardless of
output format. XLIFF / PO / JSON are now described as **three
serializations of the same model**, not three independent shapes.

Key rules:

- The CLI MUST emit all four fields (`file` / `line` / `end_line`
    / `snippet`) on every `text.hardcoded` unit. Missing fields
    use sentinel values (`line: 0`, `end_line: 0`, `snippet: ""`).
- XLIFF serialization uses `<context-group name="source-context">`
    with four `<context>` children keyed by exact `context-type`
    values: `sourcefile` / `linenumber` / `endlinenumber` /
    `snippet`.
- PO serialization collapses to one `#: file:N` comment per
    captured line — `snippet` is reconstructed by the consumer
    by re-reading the source file (PO is **declared lossy**).
- JSON serialization uses exact keys `file` / `line` /
    `end_line` / `snippet`.
- A Wrapper / OmegaT MUST round-trip between XLIFF and JSON
    without loss. Round-trip with PO loses `snippet`.
- The CLI MUST NOT pick a lossy format (`po`) when the user
    requested lossless (`xliff` / `json`).

Affected files:

- `docs/shell-layer/05-config-file.md` and its Chinese translation
    — `metadata.location` / `metadata.source_context` field
    descriptions sharpened; full `source-context` subsection
    rewritten with the normative model.
- No schema change (the data model lives at the Shell layer,
    not at the IPC layer).