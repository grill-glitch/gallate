# 11. Process

> Status: **Normative**. Defines the process lifecycle of a CLI from
> Wrapper's perspective: spawn, run, cancel, terminate.

---

## Lifecycle states

```text
discover
   ↓
start
   ↓
initialize     (protocol handshake, manifest, features)
   ↓
running        (one or more operations)
   ↓
complete
   ↓
exit
```

A CLI process may run **one** or **multiple** operations in sequence.
Wrapper MAY keep the CLI alive across operations to amortize startup
cost. See [12-compatibility.md](./12-compatibility.md) for long-running
process rules.

---

## Startup

Wrapper spawns the CLI as a subprocess with:

| Channel | Setup |
| --- | --- |
| stdin | pipe (Wrapper sends request / command) |
| stdout | pipe (Wrapper reads response / events) |
| stderr | pipe or inherited (Wrapper MAY log it but MUST NOT interpret it) |
| env | Wrapper-controlled; CLI SHOULD NOT rely on env vars for project data |

Working directory defaults to the gallate.yaml Project Root. See
[10-configuration.md § Project Root](./10-configuration.md#project-root-and-cli-working-directory).

---

## Discovery sequence

```text
1. Spawn CLI
2. Announce / check protocol version
3. Read manifest       (cli manifest --yaml)
4. Read features       (cli features --yaml)
5. Read validation     (cli validation --yaml)
6. Read operation list (extended; optional)
7. Begin operations
```

Wrapper MUST NOT skip steps. See [03-discovery.md](./03-discovery.md).

---

## Operation selection (per target)

Once a Wrapper has all candidate CLIs discovered, it MUST pick
the right CLI for each candidate game / file before invoking any
operation. Two-step process:

```text
1. Read manifest.targets from each candidate CLI
2. Pick the candidate whose targets match the candidate path;
   if multiple match, call cli identify <path> on each
3. Pick the highest-confidence identify result
```

Step 2's `cli identify` is per-CLI, per-path. The Wrapper runs it
once per candidate that survived the manifest.targets filter.

If no candidate matches, the Wrapper reports "no engine recognized"
to the user. The Wrapper MUST NOT silently pick a CLI.

See [03-discovery.md § Identify](./03-discovery.md#identify) for
the response shape and confidence levels.

---

## Running an operation

```text
Wrapper                          CLI
   │                              │
   │  ── request ──────────────▶  │
   │                              │
   │  ◀── response ────────────  │   (acknowledgement + chosen id)
   │  ◀── event started ───────  │
   │  ◀── event progress ──────  │
   │  ◀── event file ──────────  │
   │  ◀── event completed ─────  │
   │                              │
   │  exit code                  │
```

After `response`, the CLI emits a stream of `event` messages. The stream
terminates with exactly one terminal event (`completed`, `cancelled`,
or implicit-failure via exit code).

---

## Cancellation

Wrapper initiates cancellation by sending a `command` message:

```yaml
type: command
command: cancel
```

Schema: [`schema/cancel-command.schema.yaml`](../schema/cancel-command.schema.yaml).

CLI behavior:

1. Stop the current operation as soon as safely possible.
2. Emit the `cancelled` event.
3. Exit with code `6`.

CLI SHOULD clean up temporary files before exiting.

---

## Signals

Signals are implementation-specific and SHOULD NOT be used as the
primary cancellation mechanism. If the CLI handles signals:

| Signal | Recommended behavior |
| --- | --- |
| `SIGTERM` | Begin graceful shutdown. Same as `cancel`. |
| `SIGINT` | Same as `SIGTERM`. |
| `SIGKILL` | OS-level; CLI cannot clean up. Wrapper SHOULD avoid. |

Wrapper SHOULD send the `cancel` command first, wait for the
`cancelled` event, and only escalate to a signal on timeout.

---

## Timeout

Wrapper MAY enforce an operation timeout. When triggered:

1. Send `cancel`.
2. Wait up to N seconds (recommended: 30s).
3. Send `SIGTERM`.
4. Wait up to M seconds (recommended: 5s).
5. Send `SIGKILL`.

The exact numbers are Wrapper choice. CLI MUST NOT assume specific
timeouts.

---

## Temporary files

CLI that creates temporary files MUST:

1. Use the system temp directory or a `.gallate-tmp/` folder under
   the Project Root.
2. Clean them up on normal exit.
4. Clean them up on cancellation.
4. Best-effort clean up on `SIGTERM`; no cleanup possible on
   `SIGKILL`.

Wrapper MAY scan `.gallate-tmp/` at startup and remove stale files
left by a previous crash.

---

## Concurrent operations

A single CLI process runs at most **one** operation at a time.
Concurrent operations require multiple CLI instances.

Wrapper MAY spawn multiple instances in parallel; each gets its own
stdin/stdout pipes and MUST use distinct operation IDs.

---

## Graceful shutdown

Wrapper that wants to close a long-lived CLI SHOULD:

1. Wait for the current operation to complete.
2. Close stdin.
3. Read remaining stdout until EOF.
4. Collect exit code.

Abrupt termination (close stdin mid-operation) is allowed but the CLI
MAY report it as a protocol error.
