# 11. Conformance

> Status: **Normative**. Defines what "compatible with the Shell
> layer" means.

A CLI that claims compatibility with the Shell-layer specification
MUST obey the rules below. Engine extensions are welcome; standard
behavior must remain stable.

---

## 11.1 Shell-layer compatibility contract

A compatible CLI MUST:

1. Accept the standard grammar `tool [op][media] project [options]`.
2. Accept `-e` (extract) and ideally `-i` (inject).
3. Accept the standard media flags `-t` (text) and `-i` (image).
4. Treat `gallate.yaml` as the sole Project Target.
5. Load `gallate.yaml` from the positional argument.
6. Resolve relative paths against the Project Root.
7. Support `--output`, `--ignore`, `--dry-run`, `-v`, `-q`, `--force`.
8. Implement `init`.
9. Apply the configuration priority CLI > YAML > engine default.
10. Apply merge semantics for `--ignore` and override semantics
    for media and `--output`.
11. Use stdout for result and stderr for diagnostics (never the other
    way around).
12. Return one of the standard exit codes (0–10).
13. Place all extension flags under `--engine.*` and document them
    separately in `--help`.
14. Refuse to overwrite an existing `gallate.yaml` from `init`
    without `--force`.

---

## 11.2 Non-requirements (engine freedom)

A compatible CLI MAY choose freely on:

- Whether to expose audio/video as `-a` / `-v` flags at the Shell
  layer (the standard requires only `text` and `image`).
- Which sub-media to declare under any media.
- Whether to support `-i` (inject) at all (a read-only extractor
  is fine; a no-extract CLI is not).
- Whether to use in-place as an output mode.
- Which script interpreter pre/post scripts use.
- The exact output directory layout inside the project.
- The exact path layout inside the output archive.
- Engine-specific flags under `--engine.*`.

---

## 11.3 Three tiers (suggested)

The Shell layer does not formalize tiers the way GCWP does (see
[GCWP § 13 Conformance](../protocol/13-conformance.md)). Most CLIs
either ship all standard behavior or none. The following loose
tiers are offered for documentation purposes only:

### Minimal

Supports `-e` and `-t` (text only). A grep-style extractor or a
scriptable CLI.

### Standard

Supports `-e` + `-i`, both standard media, the full standard flag
set, `init`, and a full project layout.

### Full

Standard + all engine-extension media exposed, full pre/post script
support, in-place, dry-run with detailed report.

These tiers are documentation only; there is no schema or
machine-checkable claim.

---

## 11.4 What "compatible with GCWP" means

A CLI that ships with Shell-layer compatibility MAY ALSO claim
[GCWP compatibility](../protocol/13-conformance.md). The two are
independent:

```text
Shell layer  →  tool is invoked from a shell
GCWP         →  tool is invoked by a Wrapper over stdin/stdout
```

A full gallate CLI implements both. A minimal CLI may implement
only the Shell layer.

See [README.md § Relationship between layers](../README.md#relationship-between-layers)
for the overall architecture.

---

## 11.5 Validation

The Shell layer does not ship with a JSON Schema (the config is
plain YAML). Validation is by inspection:

- The CLI accepts the standard grammar.
- `gallate.yaml` follows the standard top-level structure
  ([05-config-file.md](./05-config-file.md)).
- `tool --help` lists Standard Options before Engine Options.
- Exit codes 0–10 carry the standard meanings.

Engine authors SHOULD manually verify these against their
implementation.