# 06. 状态

> 状态:**规范性**。定义 CLI 按需返回的当前状态快照。

状态是**时点**查询,**补充而非取代**事件流(见 [05-事件流.md](./05-events.md))。

## Status vs Event vs Statistics

```text
Event       → 操作中,实时
Status      → 按需,"现在"快照
Statistics  → 累计,"已做了多少"
```

三者必须严格分开。

## 状态查询

`features.runtime.status` 为 true 时,CLI 必须支持状态接口。

```bash
cli status
```

CLI 正在运行操作时,返回该操作快照;空闲时 `state` 为 `idle`。

## 状态文档

Schema:[`schema/status.schema.yaml`](../../schema/status.schema.yaml)。

示例:

```json
{
  "type": "status",
  "state": "running",

  "operation": "extract",
  "phase": "extracting",

  "progress": {
    "current": 72,
    "total": 100
  },

  "current": {
    "path": "script/scene_072.bin"
  },

  "started_at": "2026-09-09T12:34:56Z"
}
```

### 字段

| 字段 | 必填 | 备注 |
| --- | --- | --- |
| `state` | ✓ | 生命周期状态(见下) |
| `operation` | 可选 | 当前操作名 |
| `phase` | 可选 | `running` 内的当前阶段 |
| `progress` | 可选 | `current` / `total` 对,`total` 可为 `null` |
| `current` | 可选 | 当前处理资源 / 文件 |
| `started_at` | 可选 | ISO-8601 时间戳 |

---

## 状态在线缆上的形式

Status **不是**事件流中的一项。它是**同步查询 / 应答**:

```text
Wrapper                          CLI
   │                              │
   │  ── status.jsonl ───▶  │   (单行,一个 JSON 对象)
   │                              │   或单独的 `cli status`
   │  ◀── single status doc ───  │   invocation
   │                              │
```

两种等价传输方式,**任选其一**,不要在同一 CLI 会话里混用:

### A. 内联状态流

```jsonl
# Wrapper → CLI stdin (running 中任意时刻)
{"type":"status-query","id":"01HSTATUS"}

# CLI → Wrapper stdout (单行,然后回到正常事件流)
{"type":"status","state":"running","operation":"extract","phase":"extracting","progress":{"current":72,"total":100}}
```

CLI 返回**恰好一条** status 文档,然后继续事件流。

### B. 单独调用

```bash
# Wrapper 启一个单独 CLI 进程(或用 side-band fd),问:
$ cli status
```

避免污染操作 stdin/stdout。Wrapper 在长操作频繁轮询时倾向此方式。

### 线缆格式

Status 文档与所有其他 GCWP 消息使用同一种线缆格式:每行一个 JSON 对象
(标准 [JSON Line Protocol](./02-core-protocol.md#json-line-protocol))。
Status 不再有独立 YAML 形式。若 `cli status` 返回 JSON Lines 以外的内容,
即为 CLI 违反协议。

---

## 状态查询消息

Schema:[`schema/status-query.schema.yaml`](../../schema/status-query.schema.yaml)。

```jsonl
{"type":"status-query","id":"01HSTATUS"}
```

Wrapper 必须带 query id,CLI 必须把同一 id 在 `type: status` 应答里回显,
便于 Wrapper 关联。

## State

标准状态:

```text
idle
preparing
running
completed
failed
cancelled
```

- `running` 是唯一有 `phase` 的状态。
- `completed` / `failed` / `cancelled` 是终态,CLI 随后退出。
- `preparing` 是收到请求到第一个 progress event 之间的窗口。

## Phase 不是 State

不要把子阶段建模为独立状态。

```text
错误:
  state = extracting

正确:
  state = running
  phase = extracting
```

Phase 都在 `running` 之下。见 [05-事件流.md § phase](./05-events.md)。

## Status vs Phase event

两者都报 phase,但:

```text
Event  phase   CLI 在阶段切换时自动发出
Status phase   Wrapper 主动询问"你现在在哪?"时读
```

Wrapper 只需 phase 转换时可订阅 `phase` event,不必轮询 status。