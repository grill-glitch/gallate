# 03. Operations

> Status: **Normative**. Defines the two standard operations and how
> media flags combine with them.

---

## 3.1 Extract

```text
-e
```

Means:

> Read the project-defined input resources and produce the
> project-defined translation assets.

```bash
tool -et ./gallate.yaml        # extract text
tool -etiav ./gallate.yaml     # extract everything
```

If no media flag is given, the project's `media:` list is used. See
[04-media.md § Default Media](./04-media.md#default-media).

---

## 3.2 Inject

```text
-i
```

Means:

> Read the project-defined translated assets and write them back
> into the project-defined input resources, producing results per
> the Output rules.

```bash
tool -it ./gallate.yaml        # inject text
tool -itai ./gallate.yaml     # inject text + audio + image (only if engine exposes -a)
```

---

## 3.3 Operation × Media matrix

The two operations are completely orthogonal to the standard media
flags. Engine-extension media are listed separately in
[04-media.md](./04-media.md).

```text
        text   image
-e      ✓      ✓
-i      ✓      ✓
```

Standard media are `text` / `image`, identified by flags `-t` /
`-i`. `audio` and `video` are engine-extension media — they MAY
appear on the CLI as `-a` / `-v` when the engine exposes them, but
they are not standardized.

---

## 3.4 Required standard operations

Every gallate CLI MUST support `-e` (extract) at minimum. `-i
` (inject) is strongly recommended; some read-only extractors may
not support it.

Engines MAY add additional operations via the
[engine-extension mechanism](./08-engine-extensions.md), but `-e` and
`-i` keep their standard meanings.

---

## 3.5 Operation with no media

```bash
tool -e ./gallate.yaml
```

Uses the project's `media:` list. See
[04-media.md § Default Media](./04-media.md#default-media).

If `media:` is also absent, the engine default is used. The engine
default is engine-specific and not standardized.

---

## 3.6 Media order has no meaning

```bash
tool -et ./gallate.yaml
tool -eit ./gallate.yaml
tool -etiv ./gallate.yaml
tool -eitav ./gallate.yaml
```

All four extract exactly the same set of media. CLI MUST treat them
identically.

---

## 3.7 Cross-reference

The mapping from a Shell-layer invocation to a GCWP request is
described in
[Protocol § Configuration](../protocol/10-configuration.md). The
Wrapper (when present) handles this translation; a CLI invoked
directly does its own translation internally.