# 07. Statistics

> Status: **Normative**. Defines the cumulative metrics a CLI emits
> about an operation.

Statistics is a **data model**, not a log. Wrapper consumes it for
project dashboards, OmegaT sidebars, and billing/quotas.

---

## Statistics document

Schema: [`schema/statistics.schema.yaml`](../schema/statistics.schema.yaml).

Example:

```jsonl
{"type":"statistics","files":{"scanned":1524,"matched":318,"processed":317,"skipped":1,"failed":0},"text":{"extracted":8421,"injected":0},"images":{"extracted":326,"injected":0},"audio":{"extracted":0,"injected":0},"video":{"extracted":0,"injected":0},"output":{"created":643,"modified":0,"bytesRead":48392012,"bytesWritten":7219382},"duration":12.84}
```

---

## Fields

| Group | Field | Notes |
| --- | --- | --- |
| files | `scanned` | Total resources examined. |
| files | `matched` | Of scanned, those that passed include/exclude. |
| files | `processed` | Successfully transformed. |
| files | `skipped` | Intentionally skipped. |
| files | `failed` | Failed transformation. |
| text | `extracted` | Strings extracted this operation. |
| text | `injected` | Strings injected this operation. |
| images | `extracted` / `injected` | Same, image media. |
| audio | `extracted` / `injected` | Same, audio media. |
| video | `extracted` / `injected` | Same, video media. |
| output | `created` | Files created. |
| output | `modified` | Files modified in place. |
| output | `bytesRead` | Total bytes read. |
| output | `bytesWritten` | Total bytes written. |
| duration | (seconds) | Wall-clock duration of the operation. |

CLI MAY add custom top-level keys. Wrapper MUST ignore unknown keys per
[12-compatibility.md](./12-compatibility.md).

---

## Machine-readable numbers only

```text
8421      ✓
8.4K      ✗   do NOT abbreviate
8,421     ✗   do NOT add thousands separators
```

---

## Custom statistics

CLI MAY add engine-specific statistics under a custom namespace:

```jsonl
{"artemis":{"controls_decoded":4218,"fonts_resolved":14}}
```

The Wrapper MUST NOT display or use these without first being taught what
they mean. Display requires a per-engine UI plugin.

---

## Statistics vs Status vs Event

```text
Status      → "What is happening now"            (snapshot)
Event       → "What just happened"               (real-time)
Statistics  → "How much has been done"           (cumulative)
```

Example:

```text
Status:
    Currently processing scene_072.bin

Statistics:
    8421 strings extracted so far
    317 files processed

Event stream (tail):
    {type: event, event: file, action: extract, path: script/scene_072.bin}
```