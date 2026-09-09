# 02. 核心协议

> 状态:**规范性**。定义 GCWP 的最低层:版本字符串、线缆格式、通道、退出码。

本章与具体操作(`extract`、`inject` …)刻意无关。操作见 [04-操作.md](./04-operations.md)。

## 通信模型

CLI 是独立进程。Wrapper 启动后通过标准 I/O 与之通信:

```text
stdin   ← Request / Command       (Wrapper 发出)
stdout  → Response / Event 流     (Wrapper 读取)
stderr  → 人类可读诊断             (给用户 / 日志)
exit    → 最终结果                 (Wrapper 读取)
```

机器可读通道(stdin / stdout)使用 **JSON Line Protocol**:每行一个 JSON 对象(标准 [JSON Lines][jsonl] / NDJSON 格式)。普通文本或自由日志**不得**出现在 stdout —— 必须走 stderr。

## JSON Line Protocol

stdin / stdout 上每条携带协议内容的行必须是一个独立 JSON 对象(标准 [JSON Lines][jsonl] / NDJSON)。接收方必须把每行作为独立文档处理:

```yaml
{type: event, event: started, operation: extract}
{type: event, event: progress, current: 10, total: 100}
{type: event, event: progress, current: 50, total: 100}
{type: event, event: completed}
```

接收方必须把每行视为独立文档。

CLI **不得**发出跨多行的 JSON 值。

YAML **不**属于 GCWP 线缆格式。YAML 留给 **Shell 层**(人类面对的 CLI 调用与 `gallate.yaml` 项目文件)。见 [00-glossary.md § YAML vs JSON](../00-glossary.md#yaml-vs-json) 中两层分工的规则。

[jsonl]: https://jsonlines.org/

## 通道

| 通道 | 方向 | 内容 |
| --- | --- | --- |
| stdin | Wrapper → CLI | 一条或多条协议消息:通常一次操作请求,可选 `cancel` 命令 |
| stdout | CLI → Wrapper | 初始 `response`,随后是事件流 |
| stderr | CLI → 用户 | 人类可读诊断,**不是**协议 |
| exit | CLI → OS | 整数退出码 |

## 协议版本

每条 GCWP 消息必须声明协议版本。版本字符串 `MAJOR.MINOR`(如 `1.0`、`1.1`、`2.0`)。

```yaml
type: protocol
name: gcwp
version: 1.0
```

### MAJOR

不兼容变更时递增。

```text
1.x → 2.x   Wrapper 可拒绝不支持的 MAJOR
```

### MINOR

向后兼容新增时递增。

```text
1.0 → 1.1   老 Wrapper 忽略未知字段
```

完整规则见 [12-兼容性.md](./12-compatibility.md)。

## 消息类型

| `type` | 方向 | 用途 |
| --- | --- | --- |
| `protocol` | 双方 | 通告 / 检查协议版本 |
| `request` | Wrapper → CLI | 操作请求 |
| `command` | Wrapper → CLI | 带外指令(当前只有 `cancel`) |
| `response` | CLI → Wrapper | 确认请求并通告操作 ID |
| `event` | CLI → Wrapper | 事件流的一项 |
| `status` | CLI → Wrapper | 对状态查询的应答(见 [06-状态.md](./06-status.md)) |
| `status-query` | Wrapper → CLI | 操作中请求状态快照 |
| `validation-result` | CLI → Wrapper | 操作中或操作后的验证发现 |

> **注意**:`validation-rules` **不是**线缆消息 —— 它是 `cli validation --yaml`
> 在发现阶段返回文档的 `type` 字段。详见
> [validation-rules.schema.yaml](../../schema/validation-rules.schema.yaml)。
> 线缆上的 payload形状是 `event: validation`,带 `severity` 与 `rule` 字段;
> 详见 [validation-result.schema.yaml](../../schema/validation-result.schema.yaml)。

所有消息类型由 [`schema/`](../../schema/) 下的 YAML Schema(JSON Schema
draft-07 语义)定义。

## 操作流(骨架)

```text
Wrapper                          CLI
   │                              │
   │  ── request ──────────────▶  │   (一次操作)
   │                              │
   │  ◀── response ────────────  │   (确认)
   │                              │
   │  ◀── event started ───────  │
   │  ◀── event progress ──────  │
   │  ◀── event file ──────────  │
   │  ◀── event warning ───────  │
   │  ◀── event completed ─────  │
   │                              │
   │  exit code                  │
```

若 Wrapper 想中止:

```text
Wrapper                          CLI
   │                              │
   │  ── command cancel ───────▶  │
   │                              │
   │  ◀── event cancelled ─────  │
   │  exit code 6                 │
```

## 退出码

标准退出码 —— 语义不得改变:

| Code | 含义 |
| --- | --- |
| `0` | 成功 |
| `1` | 操作失败 |
| `2` | 参数错误 |
| `3` | 配置错误 |
| `4` | 不支持的操作 |
| `5` | 验证失败 |
| `6` | 已取消 |
| `7` | 协议错误 |
| `8` | 内部错误 |

CLI 可定义额外退出码;标准码语义必须保留。

## 退出码 vs 事件的关系

```text
Event     → 过程信息(操作中)
Exit code → 最终结果(操作后)
```

Wrapper 必须同时考虑两者,**不得**仅由最后一个 event 推断结果。

例子:

```text
started
progress
error               (事件:流级失败)
exit 1               (进程级失败)
```

```text
started
progress
cancelled
exit 6
```