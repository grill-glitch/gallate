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
    requested a lossless one (`xliff` / `json`).

### `text.lifecycle` (when metadata is written / read) and `text.meta` (pure mapping declarations)

Two new top-level keys under `text:`:

- `lifecycle.written_on: extract` — the CLI writes the four
  metadata fields only at extract time, and preserves them verbatim
  through any number of extract → inject cycles. The source code
  is not re-read at inject time. Default; can be set to `never` to
  suppress metadata entirely.
- `lifecycle.read_on: [post-extract, pre-inject]` — the phases
  when Wrapper / OmegaT should surface the metadata. `post-extract`
  shows it to the translator; `pre-inject` shows it to QA. The
  `build` phase MUST NOT read `source-context` (the engine already
  knows the code; the captured snippet is for human consumption).
- `meta:` — purely declarative. Maps each metadata field to the
  output key it lands in (`trans-unit-attribute`,
  `context-group`, `context.linenumber`, etc.). MUST NOT add,
  rename, or remove fields; the data shape is fixed by this spec.

The `meta:` block was added per user request to make mappings
explicit when an engine uses non-default output keys. The data
shape itself stays normative; only the keys are mapped.

Affected files:

- `docs/shell-layer/05-config-file.md` and its Chinese translation
    — `lifecycle:` and `meta:` blocks added under `text:`; both EN
    and ZH `§5.2 Complete example` and `§5.8 text` block updated
    with the new fields.
- `shell-layer-examples/full-project/gallate.yaml` and
    `shell-layer-examples/minimal-project/gallate.yaml` — example
    files show `lifecycle:` and `meta:`.

Affected files (combined with the four-field model section):

- `docs/shell-layer/05-config-file.md` and its Chinese translation
    — `metadata.location` / `metadata.source_context` field
    descriptions sharpened; full `source-context` subsection
    rewritten with the normative model and the `lifecycle` /
    `meta` additions.
- No schema change (the data model lives at the Shell layer,
    not at the IPC layer).
### Engine recognition: `manifest.targets` + `cli identify`

A new capability that lets a Wrapper pick the right CLI for a
candidate game file or directory.

- `manifest.targets` — declarative block listing games,
  file / directory patterns, and binary signatures the CLI
  recognizes. Used as a coarse pre-filter.
- `cli identify <path> --yaml` — per-path inspection that
  reports which rules matched, with confidence and evidence.
  Used to disambiguate when `manifest.targets` matches
  multiple CLIs.
- New `schema/identify.schema.yaml` for the response shape.
- New `Operation selection` section in `docs/protocol/11-process.md`
  describing how a Wrapper combines `manifest.targets` and
  `cli identify` to pick a CLI.
- `docs/protocol/02-core-protocol.md` adds `identify` to the
  message-type table.
- `docs/protocol/03-discovery.md` adds a full Identify section
  (EN + ZH).
- `examples/full-cli/manifest.yaml` now carries `targets`.
- `examples/full-cli/identify.jsonl` shows the triaging
  flow across three candidate CLIs.

Affected files:

- `schema/manifest.schema.yaml` — `targets` block schema.
- `schema/gcwp.schema.yaml` — `$ref: ./identify.schema.yaml`
  added to the oneOf dispatch.
- `schema/identify.schema.yaml` — new file.
- `docs/protocol/03-discovery.md` and its Chinese translation —
  new `Identify` section.
- `docs/protocol/02-core-protocol.md` — `identify` row in
  message types table.
- `docs/protocol/11-process.md` — new `Operation selection
  (per target)` section.
- `docs/protocol/00-glossary.md` and its Chinese translation —
  `### Identify` term.
- `examples/full-cli/manifest.yaml` — sample `targets` block.
- `examples/full-cli/identify.jsonl` — new trace file.
- `examples/README.md` and `README.md` / `README.zh-CN.md` —
  tree index updated.

### Wire format: YAML Line Protocol → JSON Line Protocol

The GCWP wire format (stdin/stdout between Wrapper and CLI) was
YAML Line Protocol; it is now **JSON Line Protocol** — one JSON
object per line, the standard [JSON Lines][jsonl] / NDJSON
format.

[jsonl]: https://jsonlines.org/

The split is now:

- **Wrapper ↔ CLI** (stdin / stdout) — **JSON**. Machine-to-machine.
- **User ↔ CLI** (Shell layer) — **YAML**. The `--yaml` flag and
  the `gallate.yaml` project file stay YAML. Human-readable.

Rationale: JSON is the lingua franca of programmatic IPC; YAML
is better for files humans edit. Conflating the two leads to
either JSON leaking into user-facing files or YAML on the wire.
Each layer now uses the format it is best at.

Migration:

- All `*.yaml-stream` trace files renamed to `*.jsonl` and
  converted line-by-line to compact JSON.
- `docs/protocol/02-core-protocol.md` § "YAML Line Protocol" renamed
  to "JSON Line Protocol" with JSON examples.
- `docs/protocol/00-glossary.md` and its Chinese translation
  define "JSON Line Protocol" at § L and explain the
  Wrapper-vs-Shell layer split under § Y.
- `docs/protocol/06-status.md`'s "Wire-format conflict resolution"
  section removed; the Status document is now JSONL like every
  other wire message.
- `docs/protocol/05-events.md` updated to reference
  `#json-line-protocol`.

Affected files:

- 8 example files: `examples/{minimal,full}-cli/*.yaml-stream` →
  `*.jsonl` (git rename + content conversion).
- `docs/protocol/02-core-protocol.md` and its Chinese translation.
- `docs/protocol/00-glossary.md` and its Chinese translation.
- `docs/protocol/05-events.md` and its Chinese translation.
- `docs/protocol/06-status.md` and its Chinese translation.
- `docs/protocol/01-architecture.md` and its Chinese translation
  (architecture-diagram caption).
- `examples/README.md` (rename of `.jsonl` mention).
- `README.md` and `README.zh-CN.md` (no body change needed; the
  repository tree already says `*.jsonl` for traces and
  `*.schema.yaml` for schema definitions).

### Project Metadata: `.meta.json` (Derived Project State)

A new project-level state file that the gallate CLI writes and
maintains next to `gallate.yaml`.

- `.meta.json` is **derived state**, not config. `gallate.yaml`
  is **intent** (what the project should do); `.meta.json` records
  **what the project actually did**.
- Schema: `schema/meta.schema.yaml` with `schema_version: 1`.
  Required fields: `schema_version`, `generated_by`, `generated_at`,
  `project`, `files[]`. Optional: `hash`, `size`, `cli`, `engine`,
  `resource_id`, `timestamp`, `encoding`, `sub_media`, `extensions`.
- `files[].project` and `files[].source` are required and explicit;
  the CLI MUST NOT infer mappings from filenames or directory
  names.
- Extension fields live under `files[].extensions.<cli-id>` so
  multiple CLIs can share a project without collisions.
- The CLI MUST update `.meta.json` atomically on every operation
  that creates, modifies, moves, or deletes a project file.
- The CLI MUST NOT silently ignore drift between `.meta.json` and
  the actual project state; the recovery behavior is
  operation-defined, but never silent corruption.
- The Wrapper MAY read `.meta.json` to display resources, but
  MUST NOT re-derive mappings on its own.

Affected files:

- `docs/shell-layer/13-meta-json.md` and its Chinese translation —
  full normative chapter covering design, file location, generation,
  mapping model, stability, lifecycle, update rules, consistency,
  atomicity, CLI ownership, Wrapper responsibility, relation to
  `gallate.yaml`, user visibility, and specification scope.
- `schema/meta.schema.yaml` — new file.
- `docs/shell-layer/README.md` and its Chinese translation —
  index updated to include chapter 13.
- `shell-layer-examples/minimal-project/.meta.json` — minimal
  one-entry example.
- `shell-layer-examples/full-project/.meta.json` — full multi-entry
  example showing text / image / hardcoded, with a sub-Media
  context block on the hardcoded entry.
- `shell-layer-examples/README.md` — tree updated.
- `README.md` and `README.zh-CN.md` — `.meta.json` added to the
  contract table and the repository tree.

### Text format: XLIFF / PO removed → JSON only; position-derived unit ids

The Shell-layer text format is now **JSON only**. XLIFF and PO are no
longer standard formats.

- `text.format`'s standard value is `json`; the enum is now
  `json | engine-extension`. An engine that needs XLIFF or PO exposes
  it as an engine-extension format, and Wrapper / OmegaT are only
  required to handle JSON.
- `text.format: xliff` / `text.format: po` are no longer standard
  values. The "lossy format" rules (PO cannot carry `snippet`) are
  deleted: there is exactly one serialization, and it is lossless.
- The unit-document shape is now normative: a JSON object with
  `schema` and a flat `units` array, each unit carrying `id` /
  `source` / `target` plus the metadata keys declared in `text.meta`
  (`original_file`, `location`, `context`, `engine_path`).
- `text.meta` now maps to JSON keys rather than XLIFF attributes /
  context-groups. Defaults: `original_file` → `original_file`,
  `source_context` → `context`, `location` → `location`,
  `engine_path` → `engine_path`.

**Position-derived unit ids.** The unit `id` MUST be derived from the
unit's position in its source file — `<basename>:L<line>`, e.g.
`0083_SS_01_x.lua:L0142` — and MUST NOT be a run-order counter
(`tu-0001`, `U000001`). A counter renumbers every later unit after an
insertion and silently invalidates translation memory.

- `<line>` is 1-based, zero-padded to at least 4 digits (`L0142`).
- A second and later unit on the same line takes a `#2`, `#3`, …
  suffix, counted in source order.
- Unknown position (binary blob, obfuscated bytecode) uses the
  sentinel `line: 0`.
- Ids MUST be unique within the containing document; two source files
  sharing a basename are disambiguated by prepending path components
  joined with `_`.

This supersedes the earlier draft entries that described XLIFF / PO
serializations of the source-context model and the "lossy format"
rule.

Affected files:

- `docs/shell-layer/05-config-file.md` and its Chinese translation —
  `text:` block, field table, `meta:` mappings, a new `id`
  (position-derived) subsection, the `original-file` example, and the
  source-context section (single JSON serialization; "Lossy formats"
  removed).
- `docs/shell-layer/12-file-structure.md` and its Chinese
  translation — §12.4 rewritten as "Unit file format (JSON)" with the
  normative unit-document shape; every `.xlf` path example is now
  `.json`.
- `docs/shell-layer/13-meta-json.md` and its Chinese translation —
  `.meta.json` project paths use `.json`.
- `docs/protocol/00-glossary.md` and its Chinese translation — the
  `### XLIFF` entry is replaced by `### JSON Unit File` under `J`.
- `docs/protocol/01-architecture.md`, `03-discovery.md`,
  `08-validation.md` and their Chinese translations.
- `schema/event.schema.yaml`, `schema/validation-result.schema.yaml`,
  `schema/manifest.schema.yaml` — comment / description updates;
  `translation_unit` is now described as a position-derived id.
- `examples/full-cli/{extract,inject,validation-result}.jsonl` — `.xlf`
  paths are now `.json`, and `translation_unit` is position-derived.
- `shell-layer-examples/{full,minimal}-project/gallate.yaml` and
  `.meta.json` — `format: json`, JSON `meta:` keys, `.json` paths.

### `gallate.translation` v1: full resource-path ids, entries[], `source_context` / `state` / `notes` / `placeholders` / `provenance` / `context` (translator-helper) / `metadata`

The unit-file format graduates from "JSON only" to a versioned
**`gallate.translation`** format with explicit semantics for every
field. Three substantive changes from the earlier `units[]` shape:

1. **Container is versioned, not just unit fields.** The top level
   carries `format: "gallate.translation"`, `version: 1`, and the
   `(source, target)` language pair. The `units[]` array is renamed
   to `entries[]` (entries are the carrying shape; the term "unit"
   in the JSON clashes with `"%d"` format-specifier units).
2. **`id` is the full resource path**, not the basename. The rule
   becomes `<resource-path>:L<line>` (e.g.
   `scenario/0083_SS_01_x.lua:L0142`). The full path makes the
   "two source files share a basename" disambiguation rule
   unnecessary; only the `#<n>` suffix for "two strings on the
   same line" remains.
3. **Every entry field is classified as derived / authored /
   engine** and the spec forbids the CLI from silently recomputing
   authored fields on re-extraction. The principle is:

   > **Source is derived. Identity is derived. Translation is
   > authored. Notes are authored. Provenance is authored. Engine
   > metadata is engine-defined.**

   This becomes the new top-level section §12.13 / §12.13 设计原则
   of the file-structure chapter.

New / renamed entry fields:

- `state` — current label, not a state machine. Allowed values
  `initial` / `translated` / `reviewed` / `final` / `needs_review`.
  Labels MUST be reversible; a `final` entry MUST be allowed to
  drop to `needs_review` when the source changes.
- `source_context` — the old `context` field, renamed so the word
  "context" can be reused for translator helpers. Same four-field
  shape (`file` / `line` / `end_line` / `snippet`); same
  "extract-only, preserved through inject" lifecycle.
- `context` (new meaning) — translator-authored free-form helper
  data (`speaker` / `scene` / `location` / …). The CLI MUST NOT
  add keys to or delete keys from this object on re-extraction.
- `placeholders` — auto-detected placeholders in `source`, with
  `id` / `syntax` / `type` (`variable` / `format` / `control` /
  `ruby` / `engine`). The CLI uses this to enforce that `target`
  preserves the placeholders; mismatches fail inject.
- `notes` — translator / reviewer notes, `{text, author}` objects
  in a stack. CLI MUST NOT delete, reorder, or overwrite notes on
  re-extraction.
- `provenance` — where the current `target` came from
  (`human` / `machine` / `tm` / `mt+review`). Free-form extras
  (`model` / `method` / `score` / `source` / `match`).
- `metadata` — engine extension namespace, the only "engine"
  field. Replaces the previous `meta` (the config-side `text.meta`
  mapping declaration keeps the `meta` name).

Config-side `text.meta` mapping now has 5 default keys
(`original_file` → `original_file`, `source_context` →
`source_context`, `location` → `location`, `placeholders` →
`placeholders`, `engine_path` → `engine_path`); a new
`metadata.placeholders` flag turns placeholder emission on or off
(default `true`).

Affected files:

- `docs/shell-layer/12-file-structure.md` and its Chinese
  translation — §12.4 rewritten as three subsections
  (Container / Entry / Multiple-file layout) plus the new §12.13
  Design principle. The previous "Unit document shape" table is
  replaced by an entry-field table with a Kind column
  (derived / authored / engine).
- `docs/shell-layer/05-config-file.md` and its Chinese
  translation — `id` rule uses the full resource path; new
  subsections for `state`, `source`, `target`, `source_context`
  (renamed from `source-context`), `context` (new meaning),
  `placeholders`, `notes`, `provenance`, `metadata`; the field
  table and the §5.2 complete example are updated for the 5-key
  `meta:` and the new `metadata.placeholders` flag.
- `shell-layer-examples/{full,minimal}-project/gallate.yaml` —
  `meta:` now has 5 keys; `metadata.placeholders: true` added.
- `examples/full-cli/validation-result.jsonl` — `translation_unit`
  is now `scenario/day1/scene_001.bin:L0042` (full path).

### Single source-of-truth rule for serialization formats

The spec has now committed to a strict division of labor between
serialization formats:

- **Streaming protocol data** (events, requests, responses, status
  queries, validation findings) — **JSON Lines / NDJSON**, one
  JSON object per line. The `.jsonl` extension marks these.
- **Single-document protocol data** (discovery output: manifest,
  features, validation rules, identify, status snapshots) — **JSON**,
  one object on stdout. The `.json` extension marks these.
- **Project config** — only `gallate.yaml`, **YAML**, because
  humans edit it and comments / multi-line strings matter.
- **JSON Schema definitions** — `schema/*.schema.yaml`, **YAML**
  syntax with JSON Schema draft-07 semantics. GCWP convention; the
  `.schema.yaml` suffix signals that.

This means:

- The `--yaml` flag is **gone**. Discovery commands
  (`cli manifest`, `cli features`, `cli validation`,
  `cli identify <path>`, `cli status`) emit JSON on stdout with
  no flag.
- The `Human Mode` / `Machine Mode` glossary dichotomy is
  replaced by a single rule: protocol data is JSON, project config
  is YAML.
- The `YAML Line Protocol` glossary entry is removed; the
  `YAML vs JSON` glossary entry becomes a per-role table.
- `text/manifest.yaml` is renamed `text/manifest.json`; the YAML
  form is deprecated.

Affected files:

- `examples/full-cli/{features,manifest,validation}.yaml` →
  `examples/full-cli/{features,manifest,validation}.json`.
- `examples/minimal-cli/{features,manifest}.yaml` →
  `examples/minimal-cli/{features,manifest}.json`.
- `docs/protocol/00-glossary.md` and its Chinese translation —
  `Human Mode` / `Machine Mode` removed; `YAML vs JSON` rewritten
  as a per-role table; `YAML Line Protocol` removed.
- `docs/protocol/02-core-protocol.md` and its Chinese translation —
  `--yaml` removed; the validation-rules note rephrased.
- `docs/protocol/03-discovery.md` and its Chinese translation —
  every `cli X --yaml` removed; every discovery example rewritten
  in JSON.
- `docs/protocol/05-events.md` and its Chinese translation — every
  YAML example converted to JSON.
- `docs/protocol/06-status.md` and its Chinese translation — the
  inline status stream and the status-query example converted to
  `jsonl`.
- `docs/protocol/08-validation.md` and its Chinese translation —
  every validation-rule and validation-result example converted to
  JSON.
- `docs/protocol/11-process.md` and its Chinese translation — the
  cancel command example converted to `jsonl`.
- `docs/protocol/13-conformance.md` and its Chinese translation —
  every "features that MUST be true" example converted to JSON;
  the conformance demo invocations no longer use `--yaml`.
- `docs/shell-layer/12-file-structure.md` and its Chinese
  translation — `text/manifest.yaml` renamed to `text/manifest.json`;
  the example block converted to JSON.
- `README.md` / `README.zh-CN.md` / `examples/README.md` — the
  example trees updated; the prose explanations reworded to match
  the new format map.

> **Note on `protocol.version`:** the YAML examples used `version: 1.0`
> (a bare number) which the JSON Schema `manifest.schema.yaml` does
> not accept (it requires a `^[0-9]+\.[0-9]+$` string). The new JSON
> examples use `"1.0"` (string), which validates. This is a fix, not
> a regression — the old YAML examples would have been rejected by a
> strict CLI implementing the schema.
