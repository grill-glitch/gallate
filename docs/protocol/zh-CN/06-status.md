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
cli status --yaml
```

CLI 正在运行操作时,返回该操作快照;空闲时 `state` 为 `idle`。

## 状态文档

Schema:[`schema/status.schema.yaml`](../../schema/status.schema.yaml)。

示例:

```yaml
type: status
state: running

operation: extract

phase: extracting

progress:
  current: 72
  total: 100

current:
  path: script/scene_072.bin

started_at: 2026-09-09T12:34:56Z
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