# 10. Standard Output & Exit Codes

> Status: **Normative**. Defines how a gallate CLI uses stdout, stderr,
> and the integer exit code.

---

## 10.1 stdout / stderr separation

```text
stdout  →  operation result; machine-readable
stderr  →  progress, warnings, diagnostics, errors
```

Two hard rules:

1. **stdout contains only operation result.** No progress bars, no
   banner text, no "Extracting…" messages.
2. **stderr contains everything humans want to see.** Progress,
   warnings, diagnostics, errors.

The reason: wrapping the CLI in a script or another tool:

```bash
result=$(tool -e ./gallate.yaml -q)
echo "$result"
```

…must not have progress messages pollute the captured output.

---

## 10.2 stdout shape

The result written to stdout is engine-specific. CLI implementations
decide the format. Two conventions are encouraged but not
standardized:

- A single result path printed as the last line of stdout
  (convenient for `result=$(...)`)
- Structured YAML for engine-specific machine-readable output

The [GCWP layer](../protocol/) is a fully structured variant that
emits per-event YAML on stdout. A Wrapper driving the CLI uses
GCWP, not the Shell-layer stdout. The two are independent.

---

## 10.3 Exit codes

Standard exit codes — semantics MUST NOT change:

| Code | Meaning                  |
| ---- | ----------------------- |
| 0    | Success                 |
| 1    | General Error           |
| 2    | Invalid CLI Usage       |
| 3    | Invalid Project Configuration |
| 4    | Input Not Found         |
| 5    | Unsupported Operation   |
| 6    | Unsupported Media       |
| 7    | Extraction Failure      |
| 8    | Injection Failure       |
| 9    | Output Failure          |
| 10   | Script Failure          |

Engine Extension MAY use codes >= 11 for engine-specific failures.
The standard 0–10 codes keep their meanings.

---

## 10.4 Exit code vs events

For Shell-layer use, the exit code IS the final result. Unlike the
Protocol layer, there is no parallel event stream.

```text
operation runs
  ↓
exit code N
```

A script wrapping the CLI MUST base its error handling on the exit
code only:

```bash
if ! tool -e ./gallate.yaml; then
    case $? in
        4) echo "input not found" ;;
        6) echo "media not supported" ;;
        *) echo "other failure" ;;
    esac
fi
```

The Wrapper-driven Protocol layer has more nuance
(see [GCWP § Exit Code vs Event](../protocol/02-core-protocol.md#exit-code-vs-event)),
but the Shell layer stays simple.

---

## 10.5 In-place behavior

In-place is an **output behavior**, not a separate CLI argument.

```text
Input
  ↓
Operation
  ↓
same Input
```

The CLI MUST NOT silently turn an operation into in-place. Whether
in-place is allowed is engine-specific; engines that support it
declare so in their [features](../protocol/03-discovery.md#features)
document and MAY expose a `--engine.in-place=true` option to opt in.

If the engine does not support safe in-place modification, in-place
MUST error out with exit code 9 (Output Failure).

---

## 10.6 Verbosity and quiet vs exit code

`-v` / `-vv` / `-q` change how much the CLI prints on stderr. They
MUST NOT change the exit code.

A verbose dry run still exits 0 if the planning succeeded. A quiet
real operation still exits 1 if it failed. Verbosity is presentation
only.